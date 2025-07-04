import requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# ─── Disable only the single InsecureRequestWarning ───────────────────────────
urllib3.disable_warnings(InsecureRequestWarning)

def fetch_html_direct(url):
    resp = requests.get(url, verify=False, timeout=15)
    resp.raise_for_status()
    return resp.text

def scrape_mouser_absolute_max(part_number):
    base = "https://www.mouser.com/ProductDetail"
    url = f"{base}/{part_number}"
    print(f"\n🔍 Scraping {url}")

    try:
        html = fetch_html_direct(url)
    except Exception as e:
        print(f"  ❌ Fetch failed: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")

    # Locate the "Absolute Maximum Ratings" heading
    heading = soup.find(lambda tag: tag.name in ("h2","h3") and "Absolute Maximum Ratings" in tag.text)
    if not heading:
        print("  ❌ 'Absolute Maximum Ratings' section not found.")
        return

    # Grab the next <table> after that heading
    table = heading.find_next("table")
    if not table:
        print("  ❌ Ratings table not found under heading.")
        return

    df = pd.read_html(str(table))[0]
    print("  ✅ Parsed Absolute Maximum Ratings:\n")
    print(df.to_string(index=False))

if __name__ == "__main__":
    parts = ["BC847B", "MBRS360", "RD3L080SNFRA", "DWW-KZKG_Typ"]
    for p in parts:
        scrape_mouser_absolute_max(p)
