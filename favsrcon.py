import mmh3
import requests
import codecs
import sys
import random
import os
import re
import argparse
from urllib.parse import urlparse

# List of different User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0"
]

allowed_insecure_ips = set()
verbosity = "verbose"

def log(msg, level="info"):
    if verbosity == "quiet" and level != "critical":
        return
    print(msg)

def is_ip_address(url):
    hostname = urlparse(url).hostname
    if hostname:
        return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) is not None
    return False

def process_url(url, session, output_data):
    random_user_agent = random.choice(USER_AGENTS)
    session.headers.update({"User-Agent": random_user_agent})

    verify_ssl = True
    hostname = urlparse(url).hostname

    if is_ip_address(url) and url.startswith("https"):
        if hostname not in allowed_insecure_ips:
            try:
                choice = input(f"[!] Target {url} is an IP over HTTPS. Disable SSL verification? (y/N): ")
            except KeyboardInterrupt:
                log("\n[✘] Aborted by user.", level="critical")
                sys.exit(1)

            if choice.strip().lower() == "y":
                verify_ssl = False
                allowed_insecure_ips.add(hostname)
                log("[!] SSL verification disabled for this host.")
            else:
                log("[✘] Skipping due to SSL mismatch.")
                return

        else:
            verify_ssl = False

    try:
        response = session.get(url, timeout=10, verify=verify_ssl)
        response.raise_for_status()
        favicon = codecs.encode(response.content, "base64")
        hash_value = mmh3.hash(favicon)
        log(f"[✔] {url} - Hash: {hash_value}")
        output_data.append(f"{url} - {hash_value}")
    except requests.exceptions.RequestException as e:
        log(f"[✘] Error fetching {url}: {e}", level="critical")
        output_data.append(f"{url} - ERROR: {e}")

# --- MAIN ENTRY ---
def main():
    global verbosity

    parser = argparse.ArgumentParser(description="Favicon hash scanner")
    parser.add_argument("input", help="A URL or a file containing URLs")
    parser.add_argument("--quiet", action="store_true", help="Minimal output (only errors and summary)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output (default)")

    args = parser.parse_args()
    input_value = args.input

    verbosity = "quiet" if args.quiet else "verbose"

    output_data = []
    session = requests.Session()

    # For single URL
    if input_value.startswith("http"):
        process_url(input_value, session, output_data)

        parsed = urlparse(input_value)
        domain = parsed.hostname.replace("www.", "") if parsed.hostname else "output"
        filename = f"{domain}.txt"
        output_path = os.path.join("results", filename)

        os.makedirs("results", exist_ok=True)
        with open(output_path, "w") as output_file:
            output_file.write("\n".join(output_data))

        log(f"\nResults saved to {output_path} ✅")
        return

    # For file of URLs
    if not os.path.exists(input_value):
        with open(input_value, "w") as file:
            file.write("# Add URLs here (one per line)\n")
        log(f"File '{input_value}' created. Add URLs inside and rerun the script.", level="critical")
        sys.exit(1)

    try:
        with open(input_value, "r") as file:
            urls = [line.strip() for line in file if line.strip() and not line.startswith("#")]

        if not urls:
            log(f"No valid URLs found in {input_value}. Add some and rerun.", level="critical")
            sys.exit(1)

        for url in urls:
            process_url(url, session, output_data)

    except FileNotFoundError:
        log(f"Error: File '{input_value}' not found.", level="critical")
        sys.exit(1)

    if output_data:
        os.makedirs("results", exist_ok=True)
        output_path = os.path.join("results", "output.txt")
        with open(output_path, "w") as output_file:
            output_file.write("\n".join(output_data))
        log(f"\nResults saved to {output_path} ✅")
    else:
        log("\nNo results to save. All targets skipped or failed. ❌", level="critical")

if __name__ == "__main__":
    main()
