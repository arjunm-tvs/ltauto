from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup

# Set your local ChromeDriver path
CHROMEDRIVER_PATH = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\chromedriver-win64\chromedriver.exe"

def create_driver():
    opts = Options()
    opts.headless = True  # Run without opening a visible window
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=opts)

def scrape_digikey_absolute_max_selenium(part_number, driver):
    print(f"\n🔍 Digi-Key lookup for {part_number}")

    # 1) Search results page
    search_url = f"https://www.digikey.com/en/products/result?keywords={part_number}"
    driver.get(search_url)

    # 2) Find first product link
    try:
        first_link = driver.find_element("css selector", "a.apl-search__result-item-title")
        prod_url = first_link.get_attribute("href")
    except Exception:
        print("  ❌ No product found on Digi-Key.")
        return

    print(f"  → Opening product page: {prod_url}")
    driver.get(prod_url)

    # 3) Parse the page content
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    header = soup.find(lambda t: t.name in ("h2", "h3") and "Absolute Maximum Ratings" in t.text)
    if not header:
        print("  ❌ 'Absolute Maximum Ratings' section not found.")
        return

    table = header.find_next("table")
    if not table:
        print("  ❌ Ratings table not found under heading.")
        return

    df = pd.read_html(str(table))[0]
    print("  ✅ Parsed Absolute Maximum Ratings:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    driver = create_driver()

    parts = ["BC847B", "MBRS360", "RD3L080SNFRA", "DWW-KZKG_Typ"]
    for p in parts:
        scrape_digikey_absolute_max_selenium(p, driver)

    driver.quit()
