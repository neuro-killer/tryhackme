# Red Team Engagement Report: Agent Sudo (Detailed Analysis)

---

### **1. Executive Summary**

This report provides a detailed analysis of a successful red team operation conducted on **July 19, 2025**, which resulted in the complete compromise of the host at **10.10.11.80**. The engagement demonstrated how a chain of seemingly minor security oversights can be linked by an adversary to bypass security controls and achieve full administrative access.

The attack path began by exploiting an exposed **FTP service** with weak credentials. This initial foothold allowed for the exfiltration of files containing hidden data (**steganography**). Analysis of this data revealed SSH credentials for a standard user, establishing a persistent foothold on the system. The final escalation to `root` was achieved by exploiting **CVE-2019-14287**, a well-documented vulnerability in a misconfigured `sudo` policy designed to prevent this exact outcome.

The success of this operation underscores that security is a holistic process; a failure in one area (e.g., password policy) can invalidate controls in another (e.g., user permissions).

---

### **2. Technical Kill Chain Narrative**

The attack progressed through a logical sequence of reconnaissance, initial access, and privilege escalation.

#### **2.1. Reconnaissance & Initial Enumeration** 🕵️

The objective of reconnaissance is to map the target's attack surface. The Nmap scan identified three key services, each with distinct potential for exploitation:

* **21/tcp (FTP):** This is a high-value target for reconnaissance. FTP services are notorious for misconfigurations, including anonymous access or, as in this case, accounts with weak, easily guessable passwords. The identified `vsftpd 3.0.3` version is not immediately vulnerable to a direct remote code execution exploit, shifting the focus to credential-based attacks.
* **80/tcp (HTTP):** A web server is a primary vector for exploitation. The message requiring a custom `User-Agent` string is a form of weak access control. It signals that the application has a non-standard entry point and may contain hidden functionality, making it a point of interest.
* **22/tcp (SSH):** As the standard for secure remote administration, gaining access to SSH is a primary goal. While the service itself is secure, it is the gateway for any credentials discovered elsewhere.

**Logical Conclusion:** The most promising initial entry point was the FTP service due to the high probability of weak credentials.

---

#### **2.2. Initial Access & Foothold** 🔑

The goal of this phase is to turn public information into a shell on the target system.

1.  **FTP Exploitation:** The credentials `chris:crystal` were attempted. This is a common brute-force pattern (using the username as the password) that frequently succeeds on non-critical or legacy services. The successful login immediately provided an initial foothold.

2.  **Data Exfiltration and Analysis:** Once inside the FTP server, all accessible files (`cute-alien.jpg`, `cutie.png`, `To_agentJ.txt`) were downloaded. Standard procedure dictates that any user-provided data could contain clues. `binwalk` was used on the image files because it is the standard tool for identifying embedded files or data streams (steganography). `binwalk`'s discovery of an encrypted ZIP archive inside `cutie.png` was a critical finding.

3.  **Credential Discovery Chain:** The attack followed a logical chain of clues:
    * **Crack ZIP:** The password for the ZIP archive was cracked using `john` with the `rockyou.txt` wordlist. The revealed password, `alien`, was weak and thematically related to the filenames. This is a common pattern in less secure environments.
    * **Reveal Next Clue:** The contents of the ZIP file (`To_agentR.txt`) provided the Base64 string `QXJlYTUx`. Decoding this revealed `Area51`.
    * **Uncover Final Secret:** It is logical to assume this new piece of information is a key for another locked item. `steghide` is the standard tool for steganography requiring a passphrase. Using `Area51` as the passphrase on the other downloaded file, `cute-alien.jpg`, successfully extracted the hidden message.

4.  **Achieving a Low-Privilege Shell:** The extracted message contained SSH credentials: `james:hackerrules!`. This login was successful on the SSH service (port 22), elevating access from a simple FTP session to an interactive shell as the user `james`. This constitutes a successful system foothold.

---

#### **2.3. Privilege Escalation** 🚀

With a user shell, the objective shifted to gaining root access. The first step is always to enumerate the current user's privileges.

1.  **Enumerating `sudo` Privileges:** The command `sudo -l` is standard practice for any user on a Linux system. It revealed the following rule:
    ```bash
    User james may run the following commands on agent-sudo:
        (ALL, !root) /bin/bash
    ```
2.  **Identifying the Flaw:** This rule represents a flawed **deny-list** security model. The administrator's *intent* was to allow `james` to run `bash` as any user *except* for `root`. However, this type of rule is notoriously easy to bypass. The presence of `(ALL, !root)` immediately flags a potential vulnerability, specifically CVE-2019-14287.

3.  **Exploiting CVE-2019-14287:** This vulnerability exists because `sudo` versions prior to 1.8.28 incorrectly handle user ID `-1` (or its unsigned equivalent, `4294967295`). When `sudo` is asked to run a command as user `-1`, its user-lookup functions can resolve this to UID `0` (root). The `!root` check in the sudoers policy fails to catch this, allowing the command to execute with root privileges.

4.  **Executing the Exploit:** The command `sudo -u#-1 /bin/bash` leverages this flaw directly. The system granted a `bash` shell, and a subsequent `whoami` check would confirm the user is now `root`. This action successfully bypassed the intended security control and achieved the final objective of full system compromise.

---

### **3. Vulnerabilities and Actionable Recommendations**

1.  **V-01: Insecure Service Configuration (Critical)**
    * **Description:** The FTP service used weak, default-like credentials. Unencrypted protocols like FTP also transmit credentials in cleartext, posing a risk of interception.
    * **Recommendation:**
        * Disable the FTP service if it is not business-critical.
        * If required, replace it with **SFTP (SSH File Transfer Protocol)**, which is encrypted by default.
        * Enforce a **strong password policy** across all accounts and integrate user management with a central directory (e.g., LDAP, Active Directory) to ensure compliance.

2.  **V-02: Information Disclosure via Insecure Data Storage (High)**
    * **Description:** Critical secrets (SSH credentials) were stored insecurely within publicly accessible files using trivial steganography.
    * **Recommendation:**
        * Implement a **secrets management** solution (e.g., HashiCorp Vault, AWS/GCP/Azure secret managers) for all credentials and API keys.
        * Conduct **developer training** on secure coding practices, explicitly forbidding the storage of secrets in files.
        * Integrate automated **secret scanning** tools into your CI/CD pipeline to detect exposed credentials before they reach production.

3.  **V-03: Sudo Privilege Escalation via Misconfiguration (Critical)**
    * **Description:** The sudoers policy used a flawed deny-list approach, which was bypassed by the known vulnerability CVE-2019-14287.
    * **Recommendation:**
        * **Patch Immediately:** Update the `sudo` package to version `1.8.28` or later to remediate the CVE.
        * **Adopt Allow-List Policies:** Never use `!` in sudoer rules. Instead, follow the **Principle of Least Privilege** by explicitly granting only the specific commands needed for a user to perform their role. For example: `james ALL = /usr/bin/specific_command`.
