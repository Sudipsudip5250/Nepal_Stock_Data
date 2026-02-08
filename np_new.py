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
GITHUB_TOKEN = os.getenv("TOKEN_GITHUB") # Corrected typo
GITHUB_USER_EMAIL = os.getenv("USER_EMAIL_GITHUB")

# --- Determine Repository Names and Paths ---
# The actual name of the public repository to clone
CANONICAL_REPO_NAME = "Nepal_Stock_Data"

# Determine the local folder name for the cloned repository
# Prioritize REPO_GITHUB from .env, otherwise default to the canonical name
LOCAL_REPO_FOLDER_NAME = os.getenv("REPO_GITHUB")
# Modified: Check if LOCAL_REPO_FOLDER_NAME is None OR an empty string
if not LOCAL_REPO_FOLDER_NAME:
    LOCAL_REPO_FOLDER_NAME = CANONICAL_REPO_NAME
    print(f"✅ REPO_GITHUB not found or empty in .env, defaulting local folder name to '{LOCAL_REPO_FOLDER_NAME}'.")
else:
    print(f"✅ Local folder name set to '{LOCAL_REPO_FOLDER_NAME}' .")

# --- Verify GitHub Token and Set Defaults for Git User ---
push_enabled = True
if not GITHUB_TOKEN:
    print("⚠️ Warning: GITHUB_TOKEN environment variable is not set. Git push operations will be skipped.")
    push_enabled = False

if not GITHUB_USER_EMAIL:
    GITHUB_USER_EMAIL = "you@example.com"
    print(f"⚠️ Warning: GITHUB_USER_EMAIL not set, defaulting to '{GITHUB_USER_EMAIL}'.")

if not GITHUB_USERNAME:
    GITHUB_USERNAME = "Your Name"
    print(f"⚠️ Warning: GITHUB_USERNAME not set, defaulting to '{GITHUB_USERNAME}'.")

# --- Determine Root Path and Repository Path ---
IN_COLAB = 'google.colab' in sys.modules # Detect if we're in Colab
if IN_COLAB:
    root_path = "/content"
else:
    try:
        root_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root_path = os.getcwd()

print(f"📂 Root path set to: {root_path}")

# Full path to the local repository folder
repo_folder_path = os.path.join(root_path, LOCAL_REPO_FOLDER_NAME)

# --- Step 1: Clone Repository if it doesn't exist ---
if not os.path.exists(repo_folder_path) or not os.path.isdir(repo_folder_path):
    print(f"🔍 Repository folder '{repo_folder_path}' does not exist. Proceeding to clone.")
    
    # Use the CANONICAL_REPO_NAME for the source URL and LOCAL_REPO_FOLDER_NAME for the target directory
    clone_cmd = f"git clone https://github.com/Sudipsudip5250/{CANONICAL_REPO_NAME}.git \"{repo_folder_path}\""
    print(f"Executing clone command: {clone_cmd}")
    result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Clone failed: {result.stderr}")
        print("Exiting as repository setup failed.")
        sys.exit(1)
    else:
        print("✅ Cloned successfully!")
        if result.stdout:
            print(f"Clone output: {result.stdout}")
else:
    print(f"✅ Repository folder '{repo_folder_path}' found!")

# --- Change Directory into the Cloned Repository ---
print(f"Current working directory before chdir: {os.getcwd()}")
try:
    os.chdir(repo_folder_path)
    print(f"Changed current directory to: {os.getcwd()}")
except OSError as e:
    print(f"❌ Cannot change directory to '{repo_folder_path}': {e}. Exiting.")
    sys.exit(1)

# --- Step 3: Set Git user credentials ---
os.system(f"git config --local user.email \"{GITHUB_USER_EMAIL}\"") # Use quotes for email
os.system(f"git config --local user.name \"{GITHUB_USERNAME}\"") # Use quotes for username
print("Git user credentials configured.")

# --- Step 4: Prepare for Git Push (if enabled) ---
if push_enabled:
    print("Git push operations are enabled (GITHUB_TOKEN found).")
else:
    print("Git push operations are disabled (GITHUB_TOKEN not set).")

# --- Define Base Data Paths ---
# BASE_FOLDER will be created relative to the current working directory (repo_folder_path)
BASE_FOLDER = "Nepse_Data"
# listed_company path is relative to the current working directory (repo_folder_path)
listed_company = os.path.join("other_nepse_detail", "listed_company.csv")

# GitHub raw file URL for downloading the listed companies list if not found locally
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/Sudipsudip5250/{CANONICAL_REPO_NAME}/main/{listed_company}"

# --- Check and Download listed_company.csv ---
print(f"Checking for listed company file at: {os.path.join(os.getcwd(), listed_company)}")
if not os.path.exists(listed_company):
    print(f"⚠️ File '{listed_company}' not found locally within the cloned repository! Attempting to download from GitHub...")
    try:
        # Ensure the directory for listed_company.csv exists before writing
        os.makedirs(os.path.dirname(listed_company), exist_ok=True)
        
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        with open(listed_company, "wb") as file:
            file.write(response.content)

        print(f"✅ Successfully downloaded '{listed_company}' from GitHub.")

    except requests.RequestException as e:
        print(f"❌ Failed to download file '{listed_company}': {e}")
        sys.exit(1)  # Exit script if download fails
else:
    print(f"✅ File '{listed_company}' found locally.")

# --- Read the CSV file ---
with open(listed_company, 'r', encoding='utf-8') as file:
    reader = list(csv.reader(file))
    categories = reader[0]
    symbols_by_category = list(zip(*reader[1:]))
print("✅ Successfully loaded symbol data.")

# --- Configure Selenium WebDriver ---
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

# --- Process Each Category and its Symbols ---
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

        filename_safe = symbol.replace('/', '_')
        csv_filename = os.path.join(category_folder, f"{filename_safe}.csv")

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

        while True:
            page_count += 1
            print(f"🔍 Scraping {symbol} - processing page {page_count}")
            try:
                table = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='cpricehistory']//table")))
                rows = table.find_elements(By.XPATH, ".//tbody/tr")

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 9:
                        continue

                    data = [cell.text.strip() for cell in cells]
                    row_date = data[1]

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

        if new_data:
            new_df = pd.DataFrame(new_data, columns=["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"])
            latest_scraped_date = new_df["Date"].max()

            if os.path.exists(csv_filename):
                updated_df = pd.concat([new_df, existing_df], ignore_index=True)
            else:
                updated_df = new_df

            updated_df["Date"] = pd.to_datetime(updated_df["Date"], format="%Y-%m-%d", errors="coerce")
            updated_df = updated_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
            updated_df["S.N."] = updated_df.index + 1
            cols = ["S.N.", "Date", "Open", "High", "Low", "Ltp", "% Change", "Qty", "Turnover"]
            updated_df = updated_df[cols]

            updated_df.to_csv(csv_filename, index=False, encoding='utf-8')
            print(f"✅ New data added for {symbol} in {csv_filename}")
            
            sector_has_updates = True
            sector_updated_symbols.append(symbol)
            
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
        
        result = subprocess.run("git add --all", shell=True, capture_output=True, text=True)
        print(f"Git add output: {result.stdout}")
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            continue

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