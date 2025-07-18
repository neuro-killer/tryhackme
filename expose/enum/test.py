import requests
import sys

def check_urls(urls):
    """
    Checks the HTTP status code for a given list of URLs.

    Args:
        urls (list): A list of strings, where each string is a URL to check.
    """
    print("[*] Starting URL status check...")
    print("-" * 30)

    for url in urls:
        try:
            # Send a GET request to the URL
            response = requests.get(url, timeout=5) # Set a timeout to prevent hanging
            status_code = response.status_code
            print(f"[+] {url}: Status {status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[-] {url}: Connection refused or host unreachable.")
        except requests.exceptions.Timeout:
            print(f"[-] {url}: Request timed out.")
        except requests.exceptions.RequestException as e:
            # Catch any other requests-related errors
            print(f"[-] {url}: An error occurred - {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"[-] {url}: An unexpected error occurred - {e}")

    print("-" * 30)
    print("[*] URL status check finished.")

if __name__ == "__main__":
    # Define the base URL from the target
    BASE_URL = "http://10.10.186.2:1337/"
    PHPMYADMIN_URL = "http://10.10.186.2:1337/phpmyadmin/"

    # List of specific files and paths to check, based on your previous enumeration
    # and common developer oversight patterns.
    target_paths = [
        # Common web application config files (root directory)
        "config.php",
        "settings.php",
        "database.php",
        "connection.php",
        "connect.php",
        "credentials.php",
        "db.php",
        ".env",
        "wp-config.php", # Though not WordPress, it's a common config file name

        # Backup files (root directory)
        "index.php.bak",
        "index.php.old",
        "index.php~",
        "config.php.bak",
        "config.php.old",
        "config.php~",
        "backup.zip",
        "website.zip",
        "archive.tar.gz",
        "web.config.bak", # For Windows servers, but good to check

        # Files related to "Expose Web Challenge" theme
        "expose.php",
        "challenge.php",
        "webchallenge.php",
        "secret.php",
        "secret.txt",
        "passwords.txt",
        "flag.txt", # Common CTF flag location
        "user.txt", # Common CTF flag location
        "root.txt", # Common CTF flag location
    ]

    # Construct full URLs for the root directory
    full_urls_root = [BASE_URL + path for path in target_paths]

    # Specific phpMyAdmin related paths (already checked some, but re-including for completeness)
    phpmyadmin_paths = [
        "config.inc.php", # phpMyAdmin's main config
        "setup/",         # phpMyAdmin setup directory
        "setup.php",      # phpMyAdmin setup script
        "docs/",          # Documentation folder, sometimes has interesting files
        "examples/",      # Example configurations, sometimes left with defaults
        "libraries/config.default.php", # Default config, might reveal structure
    ]

    # Construct full URLs for the phpMyAdmin directory
    full_urls_phpmyadmin = [PHPMYADMIN_URL + path for path in phpmyadmin_paths]

    # Combine all URLs
    all_urls_to_check = full_urls_root + full_urls_phpmyadmin

    # Execute the check
    check_urls(all_urls_to_check)
