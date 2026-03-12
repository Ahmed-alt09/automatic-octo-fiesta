import os
import requests
import concurrent.futures
from tqdm import tqdm

API_URL = "https://api.wordpress.org/plugins/info/1.2/"
PER_PAGE = 1000
OUTPUT_DIR = "plugins"

MIN_INSTALLS = 1000
MAX_INSTALLS = 6000
MAX_WORKERS = 30

def fetch_plugins():
"""Fetch plugin metadata from the WordPress.org API."""
all_plugins = []
page = 1

print("[*] Starting plugin metadata collection...\n")

while True:
    params = {
        "action": "query_plugins",
        "request[per_page]": PER_PAGE,
        "request[page]": page
    }

    try:
        resp = requests.get(API_URL, params=params, timeout=30)

        if resp.status_code != 200:
            print(f"[!] Failed to fetch page {page}: HTTP {resp.status_code}")
            break

        data = resp.json()
        plugins = data.get("plugins", [])

        if not plugins:
            break

        all_plugins.extend(plugins)

        print(f"[+] Page {page}: +{len(plugins)} plugins (total: {len(all_plugins)})")

        page += 1

    except Exception as e:
        print(f"[!] Error fetching page {page}: {e}")
        break

print(f"\n[*] Metadata collection complete: {len(all_plugins)} plugins found\n")

return all_plugins

def filter_plugins(plugins):
"""Filter plugins by active install range."""
filtered = [
p for p in plugins
if MIN_INSTALLS <= p.get("active_installs", 0) <= MAX_INSTALLS
]

print(f"[*] Plugins in install range {MIN_INSTALLS} - {MAX_INSTALLS}: {len(filtered)}\n")

return filtered

def download_plugin(session, slug):
"""Download a single plugin ZIP file."""
url = f"https://downloads.wordpress.org/plugin/{slug}.zip"
filepath = os.path.join(OUTPUT_DIR, f"{slug}.zip")


if os.path.exists(filepath):
    return

try:
    resp = session.get(url, stream=True, timeout=30)

    if resp.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(65536):
                if chunk:
                    f.write(chunk)

except Exception:
    pass

def main():
os.makedirs(OUTPUT_DIR, exist_ok=True)

plugins = fetch_plugins()

filtered_plugins = filter_plugins(plugins)

if not filtered_plugins:
    print("[!] No plugins match the install range.")
    return

slugs = [plugin["slug"] for plugin in filtered_plugins]

print(f"[*] Starting download of {len(slugs)} plugins using {MAX_WORKERS} threads...\n")

session = requests.Session()

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(download_plugin, session, slug)
        for slug in slugs
    ]

    for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        pass

print("\n[✓] All downloads completed.")
print(f"[*] Plugins saved in: {OUTPUT_DIR}/")

if **name** == "**main**":
main()
