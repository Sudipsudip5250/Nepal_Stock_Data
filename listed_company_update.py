import csv
import os
import time
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
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

IN_COLAB = 'google.colab' in sys.modules

# Determine root path depending on environment
if IN_COLAB:
    root_path = "/content"
else:
    try:
        root_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        root_path = os.getcwd()

print(f"📂 Root path set to: {root_path}")
os.chdir(root_path)

# Step 1: Set Git user credentials
os.system(f"git config --global user.email {GITHUB_USER_EMAIL}")
os.system(f"git config --global user.name {GITHUB_USERNAME}")

# Define paths
listed_company_path = "other_nepse_detail/listed_company.csv"

# Mapping from website sector names to CSV sector names (with underscores)
SECTOR_MAPPING = {
    "Commercial Bank": "Commercial_Banks",
    "Corporate Debentures": "Corporate_Debentures",
    "Development Bank": "Development_Bank_Limited",
    "Finance": "Finance",
    "Government Bonds": "Government_Bonds",
    "Hotel & Tourism": "Hotels_And_Tourism",
    "Hydropower": "Hydro_Power",
    "Investment": "Investment",
    "Life Insurance": "Life_Insurance",
    "Manufacturing and Processing": "Manufacturing_And_Processing",
    "Microfinance": "Microfinance",
    "Mutual Fund": "Mutual_Fund",
    "Non-Life Insurance": "Non-Life_Insurance",
    "Others": "Others",
    "Preference Share": "Preference_Share",
    "Promotor Share": "Promotor_Share",
    "Promoter Share": "Promoter_Share",
    "Trading": "Tradings"
}

print("="*60)
print("🔄 Starting Listed Company Update Process")
print("="*60)

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
wait = WebDriverWait(driver, 10)

url = "https://www.sharesansar.com/company-list"
driver.get(url)
time.sleep(3)

def _dismiss_overlays(driver):
    # Best-effort close for common overlays/banners that can intercept clicks
    selectors = [
        "[id*='cookie'] button",
        "[class*='cookie'] button",
        "[id*='consent'] button",
        "[class*='consent'] button",
        "[class*='modal'] [aria-label='Close']",
        "[class*='modal'] .close",
        "[class*='popup'] .close",
        "[class*='overlay'] .close",
    ]
    for sel in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in elements:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(0.5)
                    except Exception:
                        driver.execute_script("arguments[0].click()", el)
                        time.sleep(0.5)
        except Exception:
            continue

def safe_click(driver, wait, by, locator, timeout=10):
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))
    except TimeoutException:
        pass
    try:
        element.click()
        return
    except ElementClickInterceptedException:
        _dismiss_overlays(driver)
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        driver.execute_script("arguments[0].click()", element)

# Dictionary to store symbols by sector
sector_data = defaultdict(list)

# Get all sector options from the dropdown
try:
    sector_dropdown = wait.until(EC.presence_of_element_located((By.ID, "sector")))
    sector_select = Select(sector_dropdown)
    all_sectors = [(option.text, option.get_attribute("value")) for option in sector_select.options]
    print(f"✅ Found {len(all_sectors)} sectors to process")
except Exception as e:
    print(f"❌ Error finding sector dropdown: {e}")
    driver.quit()
    exit(1)

# Process each sector
for sector_name, sector_value in all_sectors:
    print(f"\n{'='*60}")
    print(f"🔍 Processing Sector: {sector_name}")
    print(f"{'='*60}")
    
    # Map sector name to CSV format
    csv_sector_name = SECTOR_MAPPING.get(sector_name, sector_name.replace(" ", "_").replace("&", "And"))
    
    try:
        # Select the sector
        sector_dropdown = driver.find_element(By.ID, "sector")
        sector_select = Select(sector_dropdown)
        sector_select.select_by_value(sector_value)
        time.sleep(1)
        
        # Click the search button
        safe_click(driver, wait, By.ID, "btn_listed_submit")
        print(f"⏳ Waiting for data to load...")
        time.sleep(3)
        
        # Change entries to 50
        try:
            length_select = wait.until(EC.presence_of_element_located((By.NAME, "myTable_length")))
            Select(length_select).select_by_value("50")
            print(f"✅ Set display to 50 entries")
            time.sleep(2)  # Wait for table to reload
        except Exception as e:
            print(f"⚠️ Could not change display length: {e}")
        
        page_count = 0
        sector_symbols = []
        
        # Loop through all pages
        while True:
            page_count += 1
            print(f"📄 Scraping page {page_count}...")
            
            try:
                # Wait for table to load
                table = wait.until(EC.presence_of_element_located((By.ID, "myTable")))
                rows = table.find_elements(By.XPATH, ".//tbody/tr")
                
                page_symbols = []
                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            # Symbol is in the second column (index 1)
                            symbol_cell = cells[1]
                            symbol_link = symbol_cell.find_element(By.TAG_NAME, "a")
                            symbol = symbol_link.text.strip()
                            if symbol:
                                page_symbols.append(symbol)
                    except Exception:
                        continue
                
                if page_symbols:
                    sector_symbols.extend(page_symbols)
                    print(f"✅ Found {len(page_symbols)} symbols on page {page_count}")
                else:
                    print(f"⚠️ No symbols found on page {page_count}")
                
            except Exception as e:
                print(f"⚠️ Error reading table: {e}")
                break
            
            # Check if there's a next page
            try:
                next_button = driver.find_element(By.ID, "myTable_next")
                
                # Check if next button is disabled
                if "disabled" in next_button.get_attribute("class"):
                    print(f"⏹️ Reached last page (page {page_count})")
                    break
                
                # Click next button
                safe_click(driver, wait, By.ID, "myTable_next")
                print(f"➡️ Moving to next page...")
                time.sleep(2)  # Wait for next page to load
                
            except Exception as e:
                print(f"⏹️ No more pages available")
                break
        
        # Sort symbols alphabetically
        sector_symbols.sort()
        
        # Store in dictionary
        if sector_symbols:
            sector_data[csv_sector_name] = sector_symbols
            print(f"✅ Total symbols collected for {csv_sector_name}: {len(sector_symbols)}")
            print(f"📊 Symbols: {', '.join(sector_symbols[:10])}{'...' if len(sector_symbols) > 10 else ''}")
        else:
            print(f"⚠️ No symbols found for {csv_sector_name}")
    
    except Exception as e:
        print(f"❌ Error processing sector {sector_name}: {e}")
        continue

driver.quit()

print(f"\n{'='*60}")
print(f"📝 Writing data to CSV file")
print(f"{'='*60}")

# Find the maximum number of rows needed
max_rows = max([len(symbols) for symbols in sector_data.values()]) if sector_data else 0

# Sort sectors to maintain consistent order
# Preserve original order from SECTOR_MAPPING but only include scraped sectors
ordered_sectors = []
for original_sector in SECTOR_MAPPING.values():
    if original_sector in sector_data:
        ordered_sectors.append(original_sector)

# Add any new sectors not in the mapping
for sector in sorted(sector_data.keys()):
    if sector not in ordered_sectors:
        ordered_sectors.append(sector)

print(f"✅ Found {len(ordered_sectors)} sectors with data")
print(f"✅ Maximum rows needed: {max_rows}")

# Write to CSV
try:
    with open(listed_company_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header (sector names)
        writer.writerow(ordered_sectors)
        
        # Write data rows
        for row_idx in range(max_rows):
            row_data = []
            for sector in ordered_sectors:
                symbols = sector_data.get(sector, [])
                if row_idx < len(symbols):
                    row_data.append(symbols[row_idx])
                else:
                    row_data.append('')  # Empty cell if no more symbols
            writer.writerow(row_data)
    
    print(f"✅ Successfully wrote data to {listed_company_path}")
    
    # Display summary
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    for sector in ordered_sectors:
        count = len(sector_data[sector])
        print(f"  {sector}: {count} companies")
    
except Exception as e:
    print(f"❌ Error writing to CSV: {e}")
    exit(1)

# Git operations
print(f"\n{'='*60}")
print(f"💾 Committing changes to Git")
print(f"{'='*60}")

# Git add
result = subprocess.run("git add other_nepse_detail/listed_company.csv", shell=True, capture_output=True, text=True)
print(f"Git add output: {result.stdout}")
if result.returncode != 0:
    print(f"❌ Git add failed: {result.stderr}")
    exit(1)

# Git commit
commit_message = "Updated listed company data"
result = subprocess.run(f'git commit -m "{commit_message}" --allow-empty', shell=True, capture_output=True, text=True)
print(f"Git commit output: {result.stdout}")
if result.returncode != 0:
    print(f"❌ Git commit failed: {result.stderr}")
    exit(1)

# Git push (only if token is available)
if push_enabled:
    result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
    print(f"Git push output: {result.stdout}")
    if result.returncode != 0:
        print(f"❌ Git push failed: {result.stderr}")
        print("Hint: Ensure GITHUB_TOKEN is set in your .env file and has write access to the repository for pushing changes.")
    else:
        print(f"✅ Successfully pushed changes to repository.")
else:
    print(f"⚠️ Git push skipped because GITHUB_TOKEN is not set or push is disabled.")

print(f"\n{'='*60}")
print(f"🎉 Listed Company Update Completed Successfully!")
print(f"{'='*60}")
