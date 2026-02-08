import csv
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
import sys
from dotenv import load_dotenv
import subprocess

load_dotenv()
# GitHub Credentials
GITHUB_USERNAME = os.getenv("USERNAME_GITHUB")
GITHUB_TOKEN = os.getenv("TOKEN_GITHUB")
GITHUB_REPO = os.getenv("REPO_GITHUB")
GITHUB_USER_EMAIL = os.getenv("USER_EMAIL_GITHUB")

# Verify GITHUB_TOKEN is set and enable/disable push accordingly
push_enabled = True
if not GITHUB_TOKEN:
    print("⚠️ Warning: GITHUB_TOKEN environment variable is not set. Git push operations will be skipped.")
    push_enabled = False

IN_COLAB = 'google.colab' in sys.modules # Detect if we're in Colab
# Determine root path depending on environment
if IN_COLAB:
    root_path = "/content"
else:
    try:
        root_path = os.path.dirname(os.path.abspath(__file__)) # For local: use script location or current working directory
    except NameError:
        # For interactive sessions like Jupyter
        root_path = os.getcwd()

print(f"📂 Root path set to: {root_path}")
os.chdir(root_path)

# Define path to repo folder
folder_path = os.path.join(root_path, GITHUB_REPO)

# Step 1: Check if the repo folder exists; skip cloning in GitHub Actions
if IN_COLAB and not os.path.exists(os.path.join(root_path, "./other_nepse_detail/listed_company.csv")):
    print("🔍 Repository folder does not exist. Proceeding to clone.")
    clone_cmd = f"git clone https://github.com/Sudipsudip5250/Nepal_Stock_Data.git"
    result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
    print(f"Clone output: {result.stdout}")
    if result.returncode != 0:
        print(f"❌ Clone failed: {result.stderr}")
        exit(1)
    print("✅ Cloned successfully!")
else:
    print("✅ Old repository folder found!")

# Step 3: Set Git user credentials
os.system(f"git config --global user.email {GITHUB_USER_EMAIL}")
os.system(f"git config --global user.name {GITHUB_USERNAME}")

# Step 4: Reset the remote URL
# Uncommand below 7 line if you are executing this locally its will set your origin remote
# remote_cmd = f'git remote set-url origin https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git'
# result = subprocess.run(remote_cmd, shell=True, capture_output=True, text=True)
# print(f"Set remote URL output: {result.stdout}")
# if result.returncode != 0:
#     print(f"❌ Failed to set remote URL: {result.stderr}")
#     exit(1)
# print("Repository remote set successfully!")

# Define base directory
BASE_FOLDER = "Nepse_Data"
listed_company = "other_nepse_detail/listed_company.csv"

# GitHub raw file URL
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Sudipsudip5250/Nepal_Stock_Data/main/other_nepse_detail/listed_company.csv"

# Check if the file exists
if not os.path.exists(listed_company):
    print(f"⚠️ File '{listed_company}' not found! Downloading from GitHub...")

    try:
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        with open(listed_company, "wb") as file:
            file.write(response.content)

        print(f"✅ Successfully downloaded '{listed_company}' from GitHub.")

    except requests.RequestException as e:
        print(f"❌ Failed to download file: {e}")
        exit(1)  # Exit script if download fails

# Read the CSV file
with open(listed_company, 'r', encoding='utf-8') as file:
    reader = list(csv.reader(file))
    categories = reader[0]
    symbols_by_category = list(zip(*reader[1:]))
print("✅ Successfully loaded symbol data.")

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # New headless mode (recommended)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--log-level=3")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 3)

# Process each category and its symbols
for category, symbols in zip(categories, symbols_by_category):
    if not category.strip():
        continue

    category_folder = os.path.join(BASE_FOLDER, category.strip())
    os.makedirs(category_folder, exist_ok=True)
    
    # Track sector-level updates
    sector_has_updates = False
    sector_latest_date = None
    sector_updated_symbols = []

    print(f"\n{'='*60}")
    print(f"🔄 Processing Sector: {category.strip()}")
    print(f"{'='*60}")

    for symbol in symbols:
        symbol = symbol.strip()
        if not symbol:
            continue

        # make a filename-safe symbol for saving (replace '/' with '_')
        filename_safe = symbol.replace('/', '_')
        csv_filename = os.path.join(category_folder, f"{filename_safe}.csv")

        # use the original symbol (lowercased) when constructing the site URL
        url = f"https://www.sharesansar.com/company/{symbol.lower()}"
        driver.get(url)
        time.sleep(1)

        try:
            price_history_button = wait.until(EC.element_to_be_clickable((By.ID, "btn_cpricehistory")))
            price_history_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Error accessing price history for {symbol}: {e}")
            continue

        try:
            select_element = wait.until(EC.presence_of_element_located((By.NAME, "myTableCPriceHistory_length")))
            Select(select_element).select_by_value("50")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Failed to change display option for {symbol}: {e}")
            continue

        # Determine the latest date already present (if any)
        latest_date = None
        existing_df = None
        if os.path.exists(csv_filename):
            try:
                existing_df = pd.read_csv(csv_filename, encoding="utf-8")
                latest_date = existing_df["Date"].astype(str).max()
                print(f"📌 {symbol}: Latest data in CSV is from {latest_date}")
            except Exception as e:
                print(f"⚠️ Error reading {csv_filename}: {e}")

        new_data = []
        page_count = 0
        stop_scraping = False

        # Loop until the "Next" button is disabled or no longer available
        while True:
            page_count += 1
            print(f"🔍 Scraping {symbol} - processing page {page_count}")
            try:
                # Re-locate the table on each page to avoid stale element reference
                table = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='cpricehistory']//table")))
                rows = table.find_elements(By.XPATH, ".//tbody/tr")

                # Iterate through rows and extract data
                for row in rows:
                    # Re-locate cells within each row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 9:
                        continue

                    data = [cell.text.strip() for cell in cells]
                    row_date = data[1]

                    # If we already have data and this row is not new, flag to stop scraping further pages
                    if latest_date and row_date <= latest_date:
                        stop_scraping = True
                        break
                    new_data.append(data)

            except Exception as e:
                print(f"⚠️ No table found for {symbol}: {e}")
                break

            if stop_scraping:
                print(f"⏸️ Stopping further scraping for {symbol} as older data encountered.")
                break

            # Try to find and click the "Next" button; if not available or disabled, break the loop
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(text(),'Next')]")
                if "disabled" in next_button.get_attribute("class").lower():
                    print("⏹️ Next button is disabled. Reached last page.")
                    break
                next_button.click()
                time.sleep(1)  # You might need to adjust the wait time
            except Exception:
                print("⏹️ No 'Next' button found or an error occurred. Ending pagination.")
                break

        if new_data:
            new_df = pd.DataFrame(new_data, columns=["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"])
            latest_scraped_date = new_df["Date"].max()  # Get the latest date from new data

            if os.path.exists(csv_filename):
                updated_df = pd.concat([new_df, existing_df], ignore_index=True)
            else:
                updated_df = new_df

            # Optional: convert Date column to datetime and sort (adjust ascending/descending as needed)
            updated_df["Date"] = pd.to_datetime(updated_df["Date"], format="%Y-%m-%d", errors="coerce")
            # Sort so that the newest dates appear first; change ascending=True for oldest-first
            updated_df = updated_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
            # Reassign S.N. sequentially starting from 1
            updated_df["S.N."] = updated_df.index + 1
            # Rearrange columns to place S.N. first
            cols = ["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"]
            updated_df = updated_df[cols]

            # Save updated CSV file
            updated_df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"✅ New data added for {symbol} in {csv_filename}")
            
            # Track sector-level updates
            sector_has_updates = True
            sector_updated_symbols.append(symbol)
            
            # Update sector latest date (keep the most recent date)
            if sector_latest_date is None or latest_scraped_date > sector_latest_date:
                sector_latest_date = latest_scraped_date

        else:
            print(f"⚠️ No new data found for {symbol}. Skipping update.")

    # Git Add, Commit, and Push for the entire sector
    if sector_has_updates:
        print(f"\n{'='*60}")
        print(f"💾 Committing updates for sector: {category.strip()}")
        print(f"📊 Updated {len(sector_updated_symbols)} companies: {', '.join(sector_updated_symbols)}")
        print(f"{'='*60}\n")
        
        # Git add only the specific sector directory
        sector_directory = os.path.join(BASE_FOLDER, category.strip())
        result = subprocess.run(f'git add "{sector_directory}"', shell=True, capture_output=True, text=True)
        print(f"Git add output: {result.stdout}")
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            continue

        # Create commit message with sector name and latest date
        sector_name = category.strip().replace('_', ' ')
        commit_message = f'Updated {sector_name} data up to {sector_latest_date}' if sector_latest_date else f'Updated {sector_name} data'
        
        result = subprocess.run(f'git commit -m "{commit_message}" --allow-empty', shell=True, capture_output=True, text=True)
        print(f"Git commit output: {result.stdout}")
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            continue
        
        if push_enabled:
            result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
            print(f"Git push output: {result.stdout}")
            if result.returncode != 0:
                print(f"❌ Git push failed: {result.stderr}")
                print("Hint: Ensure GITHUB_TOKEN is set in your .env file and has write access to the repository for pushing changes.")
            else:
                print(f"✅ Successfully pushed {sector_name} data to repository.\n")
        else:
            print(f"⚠️ Git push skipped for sector {sector_name} because GITHUB_TOKEN is not set or push is disabled.\n")
    else:
        print(f"⚠️ No updates found for sector: {category.strip()}\n")

driver.quit()
print("\n" + "="*60)
print("🎉 Scraping completed for all sectors!")
print("="*60)