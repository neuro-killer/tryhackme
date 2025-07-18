import argparse
import aiohttp
import asyncio
import os
from datetime import datetime
from urllib.parse import urljoin

# Common SSRF param names
ssrf_params = ["url", "path", "redirect", "dest", "next", "data", "link", "target"]

seen_paths = set()

def log(msg, file):
    print(msg)
    with open(file, "a") as f:
        f.write(msg + "\n")

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            content = await resp.read()
            return resp.status, len(content)
    except Exception:
        return None, 0

async def test_ssrf(session, base_url, path, log_file):
    ext_template = f"{base_url}/{path}?" if not path.endswith("/") else f"{base_url}/{path}"
    seen_combos = set()

    for param in ssrf_params:
        ext_url = f"{ext_template}{param}=http://example.com"
        int_url = f"{ext_template}{param}=http://127.0.0.1"

        if ext_url in seen_combos:
            continue
        seen_combos.add(ext_url)

        ext_status, ext_len = await fetch(session, ext_url)
        int_status, int_len = await fetch(session, int_url)

        log(f"  [>] Testing {param}: ext({ext_status}/{ext_len}) vs int({int_status}/{int_len})", log_file)

        if ext_status != int_status or ext_len != int_len:
            log(f"  [!!!] Potential SSRF at: {ext_template}{param}=http://127.0.0.1", log_file)

async def discover_paths(session, base_url, wordlist):
    found = []
    tasks = []
    sem = asyncio.Semaphore(500)  # For limiting concurrent fetches

    async def probe(path):
        url = urljoin(base_url + "/", path.strip())
        if url in seen_paths:
            return
        seen_paths.add(url)
        async with sem:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status not in [404]:
                        found.append((path.strip(), resp.status))
            except:
                pass

    with open(wordlist, "r") as f:
        for line in f:
            tasks.append(probe(line.strip()))

    await asyncio.gather(*tasks)
    return found

async def main():
    parser = argparse.ArgumentParser(description="SSRF Enumerator")
    parser.add_argument("-u", "--url", required=True, help="Base URL (e.g. http://10.10.10.10)")
    parser.add_argument("-p", "--port", default=80, type=int, help="Port (default: 80)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist")
    parser.add_argument("--limit", type=int, default=50, help="Max concurrent requests (default: 50)")
    args = parser.parse_args()

    full_base = f"{args.url}:{args.port}"
    log_file = f"ssrf_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log(f"[+] Starting scan against: {full_base}", log_file)
    log(f"[+] Using wordlist: {args.wordlist}", log_file)
    log(f"[+] Output log: {log_file}\n", log_file)

    conn = aiohttp.TCPConnector(limit=args.limit)
    async with aiohttp.ClientSession(connector=conn) as session:
        found_paths = await discover_paths(session, full_base, args.wordlist)
        log(f"\n[+] Found {len(found_paths)} paths:", log_file)
        for path, status in found_paths:
            log(f"[+] Found path: {full_base}/{path} (Status: {status})", log_file)

        log(f"\n[+] Testing {len(found_paths)} paths for SSRF...\n", log_file)
        for path, _ in found_paths:
            await test_ssrf(session, full_base, path, log_file)

    log("\n[+] Scan completed.\n", log_file)

if __name__ == "__main__":
    asyncio.run(main())
