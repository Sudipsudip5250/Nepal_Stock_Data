"""
This code updates the holiday calendar including weekends and public holidays,
then generates only_public_holidays.csv and public_and_weekly_holidays.csv from it.
Runs on the 1st of every month via GitHub Actions

KEY FEATURES:
1. Adds current month's weekends automatically
2. Fills in ALL missing months between calendar start and current date
3. When scraping finds holidays in any month, ensures that month has complete data
4. Dynamic pagination (no hardcoded page counts)
5. Proper wait times for reliable scraping
6. Generates separate CSV for public holidays only and all non-trading days
7. Commits and pushes only if changes are made (no empty commits)
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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

print("="*70)
print("🔄 Starting Holiday Calendar Update Process")
print("="*70)

# --- Part 0: Load existing calendar (local or GitHub) ---

CALENDAR_CSV_PATH = "other_nepse_detail/trading_calendar.csv"
CALENDAR_GITHUB_RAW = "https://raw.githubusercontent.com/Sudipsudip5250/Nepal_Stock_Data/main/other_nepse_detail/trading_calendar.csv"

if os.path.exists(CALENDAR_CSV_PATH):
    calendar_df = pd.read_csv(CALENDAR_CSV_PATH, parse_dates=['Date'])
    print(f"✅ Loaded local {CALENDAR_CSV_PATH}")
else:
    calendar_df = pd.read_csv(CALENDAR_GITHUB_RAW, parse_dates=['Date'])
    print(f"✅ Fetched calendar from GitHub")

calendar_df['date_str'] = calendar_df['Date'].dt.strftime("%Y-%m-%d")

# --- Part 1: Add Weekend Holidays (Friday & Saturday) - Complete Processing ---

print(f"\n{'='*70}")
print(f"📅 Processing Weekend Holidays - Complete Calendar Fill")
print(f"{'='*70}")

# Get the current date
current_date = datetime.now()
start_date = calendar_df['Date'].min()
end_date = calendar_df['Date'].max()

print(f"📊 Calendar date range: {start_date.date()} to {end_date.date()}")
print(f"📅 Current date: {current_date.date()}")

# Function to add weekend holidays for a given month
def add_weekend_holidays_for_month(year, month, calendar_df):
    """
    Add weekend holidays (Friday and Saturday) and weekday trading days for a given month
    """
    month_name = datetime(year, month, 1).strftime("%B %Y")
    print(f"\n🔍 Processing {month_name}...")
    
    # Get first and last day of the month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Get all dates in the month
    current = first_day
    weekends_added = 0
    weekdays_added = 0
    weekends_existing = 0
    weekends_corrected = 0
    
    while current <= last_day:
        date_str = current.strftime("%Y-%m-%d")
        weekday = current.weekday()
        
        # Friday = 4, Saturday = 5
        if weekday in [4, 5]:
            # Check if date exists in calendar
            mask = calendar_df['date_str'] == date_str
            
            if mask.any():
                # Date exists - check if it's correctly marked as weekend
                existing_row = calendar_df[mask].iloc[0]
                is_trading_day = existing_row['IsTradingDay']
                holiday_name = existing_row['HolidayName']
                
                if is_trading_day == False:
                    # Already marked as non-trading day (weekend or holiday)
                    # Only update HolidayName to "Weekend" if it's empty/None (don't overwrite public holidays)
                    if pd.isna(holiday_name) or holiday_name == '' or holiday_name == 'Weekend':
                        if holiday_name != 'Weekend':
                            calendar_df.loc[mask, 'HolidayName'] = 'Weekend'
                            weekends_corrected += 1
                            print(f"  ✏️ Corrected {date_str} to Weekend")
                        else:
                            weekends_existing += 1
                    else:
                        # Already has a public holiday name - don't overwrite it
                        weekends_existing += 1
                else:
                    # IsTradingDay is True but it's a weekend - correct it
                    calendar_df.loc[mask, 'IsTradingDay'] = False
                    calendar_df.loc[mask, 'HolidayName'] = 'Weekend'
                    weekends_corrected += 1
                    print(f"  ✏️ Corrected {date_str} to Weekend")
            else:
                # Date doesn't exist - add it as weekend
                new_row = pd.DataFrame([{
                    'Date': current,
                    'IsTradingDay': False,
                    'HolidayName': 'Weekend'
                }])
                calendar_df = pd.concat([calendar_df, new_row], ignore_index=True)
                calendar_df['date_str'] = calendar_df['Date'].dt.strftime("%Y-%m-%d")  # Update date_str
                weekends_added += 1
                print(f"  ➕ Added {date_str} as Weekend")
        else:
            # Weekday (not weekend) - ensure it exists as trading day
            mask = calendar_df['date_str'] == date_str
            if not mask.any():
                # Date doesn't exist - add it as trading day (will be updated if it's a public holiday)
                new_row = pd.DataFrame([{
                    'Date': current,
                    'IsTradingDay': True,
                    'HolidayName': ''
                }])
                calendar_df = pd.concat([calendar_df, new_row], ignore_index=True)
                calendar_df['date_str'] = calendar_df['Date'].dt.strftime("%Y-%m-%d")  # Update date_str
                weekdays_added += 1
        
        current += timedelta(days=1)
    
    # Only print summary if something changed
    if weekends_added > 0 or weekends_corrected > 0 or weekdays_added > 0:
        print(f"  📊 Summary for {month_name}:")
        if weekends_existing > 0:
            print(f"    - Existing weekends: {weekends_existing}")
        if weekends_added > 0:
            print(f"    - Added weekends: {weekends_added}")
        if weekdays_added > 0:
            print(f"    - Added weekdays: {weekdays_added}")
        if weekends_corrected > 0:
            print(f"    - Corrected weekends: {weekends_corrected}")
    
    return calendar_df, weekends_added, weekends_corrected

# CRITICAL FIX: Process ALL months from calendar start to current date
# This ensures no months are missing (like Nov/Dec 2025)

total_added = 0
total_corrected = 0

print(f"\n📌 Step 1: Filling ALL months from {start_date.date()} to {current_date.date()}...")

# Start from the beginning of the calendar
process_month = start_date.replace(day=1)
current_month_start = current_date.replace(day=1)

while process_month <= current_month_start:
    calendar_df, added, corrected = add_weekend_holidays_for_month(
        process_month.year, 
        process_month.month, 
        calendar_df
    )
    total_added += added
    total_corrected += corrected
    process_month += relativedelta(months=1)

print(f"\n✅ Complete Calendar Processing Complete:")
print(f"  - Total weekends added: {total_added}")
print(f"  - Total weekends corrected: {total_corrected}")

# Update date_str after modifications
calendar_df['date_str'] = calendar_df['Date'].dt.strftime("%Y-%m-%d")

# --- Part 2: Scrape Public Holidays from Website ---

print(f"\n{'='*70}")
print(f"🌐 Scraping Public Holidays from Website")
print(f"{'='*70}")

# Store existing holidays for comparison
existing_holidays = set(zip(
    calendar_df['date_str'],
    calendar_df['HolidayName']
))

# Determine which years to scrape
start_year = calendar_df['Date'].dt.year.max()
years_to_scrape = list(range(start_year, 2006, -1))

print(f"📅 Will scrape years: {', '.join(map(str, years_to_scrape))}")

# Configure Selenium WebDriver
print(f"\n🔧 Configuring browser...")
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(30)

print(f"✅ Browser configured successfully")

try:
    driver.get("https://nepalstock.com.np/holiday-listing")
    print(f"✅ Loaded holiday listing page")
    # Wait for Angular to render completely
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(5)  # Additional wait for ng-select to initialize

    def reset_pagination_to_page_1():
        """Reset pagination back to page 1"""
        try:
            # Try to find and click page 1 link in pagination
            # Look for the first page number link that is not disabled
            page_1_xpath = "//ul[contains(@class, 'ngx-pagination')]//li/a[contains(., '1')]"
            page_1_link = driver.find_elements(By.XPATH, page_1_xpath)
            
            if page_1_link:
                # Click the page 1 link
                driver.execute_script("arguments[0].scrollIntoView();", page_1_link[0])
                time.sleep(1)
                page_1_link[0].click()
                time.sleep(3)  # Wait for page to load
                return True
            return False
        except Exception as e:
            print(f"  ⚠️ Error resetting to page 1: {e}")
            return False

    def select_year(year):
        """Select a year from the dropdown"""
        try:
            print(f"  🔄 Selecting year {year} via dropdown...")
            
            # Click the ng-select dropdown to open it
            dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ng-select .ng-select-container"))
            )
            dropdown.click()
            time.sleep(2)  # Wait for dropdown to open
            
            # Find and click the year option
            year_xpath = f"//span[contains(@class, 'ng-option-label') and normalize-space(text())='{year}']"
            year_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, year_xpath))
            )
            year_option.click()
            
            # CRITICAL: Wait for Angular to load the data
            print(f"  ⏳ Waiting for data to load...")
            time.sleep(7)  # Increased wait time for data loading
            
            # Wait for table to be present
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )
            
            # Additional wait to ensure table is fully populated
            time.sleep(3)
            
            # Reset pagination to page 1 after year change
            print(f"  🔄 Resetting pagination to page 1...")
            reset_pagination_to_page_1()
            
            print(f"  ✅ Year {year} selected successfully")
            return True
        except Exception as e:
            print(f"  ⚠️ Error selecting year {year}: {e}")
            return False

    def has_next_page():
        """Check if Next button exists and is NOT disabled"""
        try:
            # Find the "Next" pagination button
            next_button = driver.find_element(By.XPATH, "//li[contains(@class, 'pagination-next')]")
            
            # Check if it has 'disabled' class
            is_disabled = 'disabled' in next_button.get_attribute('class')
            
            return not is_disabled
        except Exception as e:
            # If Next button not found, assume no more pages
            return False

    def click_next_page():
        """Click the Next button to go to next page"""
        try:
            # Find and click the "Next" button
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'pagination-next')]/a"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(3)  # Wait for next page to load
            return True
        except Exception as e:
            print(f"  ⚠️ Error clicking Next button: {e}")
            return False

    def scrape_table():
        """Scrape holiday data from current page"""
        try:
            tbl = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
            )
            rows = tbl.find_elements(By.TAG_NAME, "tr")[1:]
            out = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 3:
                    out.append({
                        "Holiday Date": cols[1].text.strip(),
                        "Holiday Description": cols[2].text.strip()
                    })
            return out
        except Exception as e:
            print(f"  ⚠️ Error scraping table: {e}")
            return []

    all_new = []

    for idx, year in enumerate(years_to_scrape):
        print(f"\n📅 Scraping {year}...")
        
        if not select_year(year):
            print(f"  ❌ Failed to select year {year}, skipping...")
            continue

        year_new = []
        page_number = 1

        # Scrape pages until no Next button or no more new entries
        while True:
            print(f"  📄 Scraping page {page_number}...")
            page_data = scrape_table()

            if not page_data:
                print(f"  ⏹️ No data on page {page_number}, stopping year {year}")
                break

            new_entries = []
            for e in page_data:
                key = (e['Holiday Date'], e['Holiday Description'])
                if key not in existing_holidays:
                    new_entries.append(e)
                    existing_holidays.add(key)

            if new_entries:
                print(f"  ➕ Found {len(new_entries)} new holiday(s)")
                year_new.extend(new_entries)
            else:
                print(f"  ✅ No new entries on page {page_number}")

            # Check if there's a next page
            if has_next_page():
                print(f"  ➡️ Next page available, continuing...")
                if not click_next_page():
                    print(f"  ⏹️ Failed to navigate to next page, stopping year {year}")
                    break
                page_number += 1
            else:
                print(f"  ✅ No more pages for {year} (processed {page_number} page(s))")
                break

        all_new.extend(year_new)

        # Decide whether to continue scraping earlier years
        if idx == 0:
            # Always check the second year
            continue

        if len(year_new) == 0:
            print(f"  ⏹️ No new entries in {year}, stopping further scraping")
            break

finally:
    driver.quit()
    print(f"\n✅ Browser closed")

# --- Part 3: Process New Public Holidays and Add Future Month Weekends ---

print(f"\n{'='*70}")
print(f"💾 Processing New Public Holidays")
print(f"{'='*70}")

additional_weekends_added = 0
additional_weekends_corrected = 0

if all_new:
    print(f"➕ Found {len(all_new)} new public holiday(s)")
    
    # STEP 3: Find unique months in the new holidays
    new_df = pd.DataFrame(all_new)
    new_df['Date'] = pd.to_datetime(new_df['Holiday Date'])
    
    # Get unique year-month combinations from new holidays
    new_months = new_df['Date'].apply(lambda x: (x.year, x.month)).unique()
    
    print(f"\n📌 Step 3: Checking if weekends exist for months with new holidays...")
    
    for year, month in sorted(new_months):
        month_date = datetime(year, month, 1)
        
        # Check if this month is beyond current calendar range OR if weekends don't exist
        if month_date > end_date:
            print(f"\n🆕 Found holiday in future month: {month_date.strftime('%B %Y')}")
            print(f"   Adding weekends for this month...")
            
            calendar_df, added, corrected = add_weekend_holidays_for_month(year, month, calendar_df)
            additional_weekends_added += added
            additional_weekends_corrected += corrected
        else:
            # Month is within existing range, just verify weekends exist
            first_day = datetime(year, month, 1)
            # Check if at least one weekend exists for this month
            month_str = first_day.strftime("%Y-%m")
            month_dates = calendar_df[calendar_df['date_str'].str.startswith(month_str)]
            weekends_exist = month_dates[month_dates['HolidayName'] == 'Weekend'].shape[0] > 0
            
            if not weekends_exist:
                print(f"\n⚠️ Month {month_date.strftime('%B %Y')} exists but missing weekends, adding them...")
                calendar_df, added, corrected = add_weekend_holidays_for_month(year, month, calendar_df)
                additional_weekends_added += added
                additional_weekends_corrected += corrected
    
    if additional_weekends_added > 0 or additional_weekends_corrected > 0:
        print(f"\n✅ Additional Weekend Processing Complete:")
        print(f"  - Additional weekends added: {additional_weekends_added}")
        print(f"  - Additional weekends corrected: {additional_weekends_corrected}")
    
    # Update date_str after adding future months
    calendar_df['date_str'] = calendar_df['Date'].dt.strftime("%Y-%m-%d")
    
    # STEP 4: Now merge the public holidays
    print(f"\n📌 Step 4: Merging public holidays into calendar...")
    
    for _, row in new_df.iterrows():
        d = row['Date']
        desc = row['Holiday Description']
        date_str = d.strftime("%Y-%m-%d")
        
        mask = calendar_df['Date'] == d
        if mask.any():
            # Update existing entry (might be a weekend that's now a public holiday)
            calendar_df.loc[mask, 'IsTradingDay'] = False
            calendar_df.loc[mask, 'HolidayName'] = desc
            print(f"  ✏️ Updated {date_str}: {desc}")
        else:
            # This shouldn't happen since we added the month, but handle it anyway
            new_row = pd.DataFrame([{
                'Date': d,
                'IsTradingDay': False,
                'HolidayName': desc
            }])
            calendar_df = pd.concat([calendar_df, new_row], ignore_index=True)
            print(f"  ➕ Added {date_str}: {desc}")
else:
    print("ℹ️ No new public holidays found")

# --- Part 4: Save Updated Calendar ---

print(f"\n{'='*70}")
print(f"💾 Saving Updated Calendar")
print(f"{'='*70}")

# Remove temporary column and sort
calendar_df = calendar_df.drop(columns=['date_str'], errors='ignore')
calendar_df = calendar_df.sort_values('Date', ascending=False).reset_index(drop=True)
calendar_df.to_csv(CALENDAR_CSV_PATH, index=False)

print(f"✅ Saved to {CALENDAR_CSV_PATH}")
print(f"📊 Total records: {len(calendar_df)}")

# --- Part 5: Generate only_public_holidays.csv ---

print(f"\n{'='*70}")
print(f"🔄 Generating Only Public Holidays List")
print(f"{'='*70}")

ONLY_PUBLIC_HOLIDAYS_CSV_PATH = "other_nepse_detail/only_public_holidays.csv"

print(f"\n📅 Extracting public holidays...")
public_holiday_df = calendar_df[(calendar_df['IsTradingDay'] == False) & (calendar_df['HolidayName'] != 'Weekend')]
public_holiday_df = public_holiday_df[['Date', 'HolidayName']].copy()
public_holiday_df = public_holiday_df.sort_values('Date', ascending=False).reset_index(drop=True)

print(f"📊 Found {len(public_holiday_df)} public holidays")

public_holiday_df.to_csv(ONLY_PUBLIC_HOLIDAYS_CSV_PATH, index=False)
print(f"✅ Saved to {ONLY_PUBLIC_HOLIDAYS_CSV_PATH}")

# --- Part 6: Generate public_and_weekly_holidays.csv ---

print(f"\n{'='*70}")
print(f"🔄 Generating Full Holiday List (Public and Weekends)")
print(f"{'='*70}")

FULL_HOLIDAY_LIST_CSV_PATH = "other_nepse_detail/public_and_weekly_holidays.csv"

print(f"\n📅 Extracting all non-trading days...")
full_holiday_df = calendar_df[calendar_df['IsTradingDay'] == False]
full_holiday_df = full_holiday_df[['Date', 'HolidayName']].copy()
full_holiday_df = full_holiday_df.sort_values('Date', ascending=False).reset_index(drop=True)

print(f"📊 Found {len(full_holiday_df)} non-trading days (including weekends)")

full_holiday_df.to_csv(FULL_HOLIDAY_LIST_CSV_PATH, index=False)
print(f"✅ Saved to {FULL_HOLIDAY_LIST_CSV_PATH}")

# --- Part 7: Git Operations (only if changes) ---

print(f"\n{'='*70}")
print(f"📤 Checking for Changes and Committing to Git")
print(f"{'='*70}")

files_to_check = [
    "other_nepse_detail/trading_calendar.csv",
    "other_nepse_detail/only_public_holidays.csv",
    "other_nepse_detail/public_and_weekly_holidays.csv"
]

# Add all files (git add is safe even if no changes)
for file_path in files_to_check:
    result = subprocess.run(f"git add {file_path}", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Git add failed for {file_path}: {result.stderr}")
        exit(1)

# Check for staged changes
result = subprocess.run("git diff --cached --name-only", shell=True, capture_output=True, text=True)
staged_files = result.stdout.strip().splitlines()

if staged_files:
    print(f"📝 Changes detected in: {', '.join(staged_files)}")
    commit_message = "Updated holiday lists"
    print(f"📝 Commit message: {commit_message}")

    result = subprocess.run(f'git commit -m "{commit_message}"', shell=True, capture_output=True, text=True)
    print(f"Git commit: {result.stdout if result.stdout else 'Done'}")
    if result.returncode != 0:
        print(f"❌ Git commit failed: {result.stderr}")
        exit(1)

    if push_enabled:
        result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
        print(f"Git push: {result.stdout if result.stdout else 'Done'}")
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            print("Hint: Ensure GITHUB_TOKEN is set in your .env file and has write access to the repository for pushing changes.")
        else:
            print(f"✅ Successfully pushed changes to repository.")
    else:
        print(f"⚠️ Git push skipped because GITHUB_TOKEN is not set or push is disabled.")
else:
    print("ℹ️ No changes detected - skipping commit and push")

print(f"\n{'='*70}")
print(f"🎉 Holiday Update Process Completed Successfully!")
print(f"{'='*70}")

# Final Summary
total_weekends_added = total_added + additional_weekends_added
total_weekends_corrected = total_corrected + additional_weekends_corrected
public_holidays_added = len(all_new) if 'all_new' in locals() else 0

print(f"\n📊 Final Summary:")
print(f"  - Weekend holidays added: {total_weekends_added}")
print(f"  - Weekend holidays corrected: {total_weekends_corrected}")
print(f"  - Public holidays added: {public_holidays_added}")
print(f"  - Total calendar entries: {len(calendar_df)}")
print(f"  - Public holidays extracted: {len(public_holiday_df)}")
print(f"  - Non-trading days extracted: {len(full_holiday_df)}")