import csv
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
import sys

# Determine root path depending on environment
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    root_path = "/content"
else:
    try:
        root_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root_path = os.getcwd()

print(f"📂 Root path set to: {root_path}")
os.chdir(root_path)

# Define base directory
BASE_FOLDER = "Nepse_Data"
listed_company = "other_nepse_detail/listed_company.csv"

# GitHub raw file URL for listed_company.csv
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Sudipsudip5250/Nepal_Stock_Data/main/other_nepse_detail/listed_company.csv"

# Check if the file exists
if not os.path.exists(listed_company):
    print(f"⚠️ File '{listed_company}' not found! Downloading from GitHub...")
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        response.raise_for_status()
        os.makedirs(os.path.dirname(listed_company), exist_ok=True)
        with open(listed_company, "wb") as file:
            file.write(response.content)
        print(f"✅ Successfully downloaded '{listed_company}' from GitHub.")
    except requests.RequestException as e:
        print(f"❌ Failed to download file: {e}")
        exit(1)

# Read the CSV file
with open(listed_company, 'r', encoding='utf-8') as file:
    reader = list(csv.reader(file))
    categories = reader[0]
    symbols_by_category = list(zip(*reader[1:]))
print("✅ Successfully loaded symbol data.")

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--log-level=3")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 3)

while True:
    symbol_input = input("Enter the company symbol (e.g., ADBL) or 'q'/'quit' to exit: ").strip()
    if symbol_input.lower() in ['q', 'quit']:
        print("Exiting the program.")
        break
    symbol_input = symbol_input.upper()

    # Find the category for the symbol
    category = None
    for i, sym_list in enumerate(symbols_by_category):
        cleaned_sym_list = [s.strip() for s in sym_list if s.strip()]
        if symbol_input in cleaned_sym_list:
            category = categories[i].strip()
            break

    if not category:
        print(f"❌ Symbol '{symbol_input}' not found in listed_company.csv.")
        continue

    print(f"🔍 Found symbol '{symbol_input}' in category: {category}")

    # Prepare folder and filename
    category_folder = os.path.join(BASE_FOLDER, category)
    os.makedirs(category_folder, exist_ok=True)
    filename_safe = symbol_input.replace('/', '_')
    csv_filename = os.path.join(category_folder, f"{filename_safe}.csv")

    # URL with original symbol (lowercase for compatibility)
    url = f"https://www.sharesansar.com/company/{symbol_input.lower()}"
    driver.get(url)
    time.sleep(1)

    try:
        price_history_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_cpricehistory")))
        price_history_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Error accessing price history for {symbol_input}: {e}")
        continue

    try:
        select_element = wait.until(EC.presence_of_element_located((By.NAME, "myTableCPriceHistory_length")))
        Select(select_element).select_by_value("50")
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Failed to change display option for {symbol_input}: {e}")
        continue

    # Scrape all data (full scrape, no early stop based on date)
    all_data = []
    page_count = 0

    while True:
        page_count += 1
        print(f"🔍 Scraping {symbol_input} - processing page {page_count}")
        try:
            table = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='cpricehistory']//table")))
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 9:
                    continue
                data = [cell.text.strip() for cell in cells]
                all_data.append(data)

        except Exception as e:
            print(f"⚠️ No table found for {symbol_input}: {e}")
            break

        # Check for next button
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(),'Next')]")
            if "disabled" in next_button.get_attribute("class").lower():
                print("⏹️ Next button is disabled. Reached last page.")
                break
            next_button.click()
            time.sleep(1)
        except Exception:
            print("⏹️ No 'Next' button found or an error occurred. Ending pagination.")
            break

    if all_data:
        df = pd.DataFrame(all_data, columns=["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"])
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
        df = df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        df["S.N."] = df.index + 1
        cols = ["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"]
        df = df[cols]
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"✅ Full data scraped and saved to {csv_filename}")
    else:
        print(f"⚠️ No data found for {symbol_input}.")

driver.quit()
print("🎉 Scraping completed!")