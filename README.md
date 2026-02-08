# 📈 Nepal_Stock_Data Repository

This repository contains structured datasets of companies listed in the **Nepal Stock Exchange (NEPSE)**. The data is categorized by industry sectors and scraped from public websites. It is ideal for:

- 🧠 Machine Learning & AI model training  
- 📊 Financial & statistical analysis  
- 🎓 Academic research and education  

> ⚠️ **Disclaimer:**  
> The data is scraped from public sources without formal permission. If you're the rightful owner and object to its usage, I sincerely apologize and will remove the content upon request.

---

## 📁 Folder Structure

```bash
Nepal_Stock_Data/
│
├── Nepse_Data/                      # Main dataset files categorized by sectors
│   ├── Commercial_Banks/
│   ├── Corporate_Debentures/
│   ├── Development_Bank_Limited/
│   ├── Finance/
│   ├── Government_Bonds/
│   ├── Hotels_And_Tourism/
│   ├── Hydro_Power/
│   ├── Investment/
│   ├── Life_Insurance/
│   ├── Manufacturing_And_Processing/
│   ├── Microfinance/
│   ├── Mutual_Fund/
│   ├── Non-Life_Insurance/
│   ├── Others/
│   ├── Preference_Share/
│   ├── Promoter_Share/
│   ├── Tradings/
│   └── (More sectors...)
│
├── other_nepse_detail/              # Listed company and holiday information
│   ├── listed_company.csv
│   ├── only_public_holidays.csv
│   ├── public_and_weekly_holidays.csv
│   └── trading_calendar.csv
│
├── company_full_data_scrap.py       # Scrapes full company data from sharesansar
├── listed_company_update.py         # Updates and maintains listed company information
├── nepse_data_update.py             # Main script for updating all NEPSE data
├── nepse_holiday_update.py          # Updates holiday and trading calendar data
├── requirements.txt                 # Required Python packages
├── .env.example                     # Example environment configuration
├── .gitignore                       # Git ignored files/folders
└── README.md                        # Project documentation
```

---

## 🔍 About the Project

The goal of this project is to make NEPSE data more accessible and machine-readable for:

- Developers 👨‍💻
- Data analysts 📈
- Researchers 🧑‍🔬
- Students 📚

**📌 What's Included:**

✅ Company-wise historical stock data  
✅ Sector-wise categorization (18+ sectors)  
✅ CSV files per company with OHLC (Open, High, Low, Close) data  
✅ Machine-learning-ready format  
✅ Listed company information  
✅ Holiday calendar with public holidays and weekends  
✅ Trading calendar  

All data is in **.csv** format, scraped using Python scripts.

---

## 🌐 Data Sources

The data is sourced from the following public websites:

🔗 [https://nepalstock.com.np](https://nepalstock.com.np)  
🔗 [https://www.sharesansar.com](https://www.sharesansar.com)

⚠️ No official affiliation with these platforms.

---

## 🛠️ Scripts Overview

### **▶️ nepse_data_update.py**

Main script that automates scraping of all listed company stock data.

**Features:**
- Iterates over all listed companies
- Downloads historical OHLC data
- Automatically categorizes by sector
- Stores data in `Nepse_Data/` directory
- Supports both local and Google Colab environments
- Optional GitHub integration for auto-push (requires .env configuration)

**Usage:**
```bash
python nepse_data_update.py
```

**Requirements:**
- `.env` file with GitHub credentials (optional, for auto-push feature)
- Chrome browser (for Selenium)

---

### **▶️ company_full_data_scrap.py**

Specialized script for comprehensive company data scraping.

**Features:**
- Scrapes detailed company information
- Downloads complete historical datasets
- Creates organized CSV files per company
- Handles multiple sectors
- Auto-downloads `listed_company.csv` from GitHub if missing

**Usage:**
```bash
python company_full_data_scrap.py
```

---

### **▶️ listed_company_update.py**

Maintains and updates the list of all companies traded on NEPSE.

**Features:**
- Fetches current list of listed companies
- Maintains sector mapping
- Keeps `listed_company.csv` updated
- Validates company information
- GitHub integration for version control

**Usage:**
```bash
python listed_company_update.py
```

---

### **▶️ nepse_holiday_update.py**

Updates holiday calendars and trading days.

**Features:**
- Scrapes public holidays from NEPSE website
- Generates complete holiday calendar
- Creates `only_public_holidays.csv` (public holidays only)
- Creates `public_and_weekly_holidays.csv` (all non-trading days)
- Fills missing months automatically
- Maintains `trading_calendar.csv`
- Runs monthly via GitHub Actions

**Usage:**
```bash
python nepse_holiday_update.py
```

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.7 or higher
- pip (Python package manager)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/sudipsudip5250/Nepal_Stock_Data.git
cd Nepal_Stock_Data
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: (Optional) Configure Environment Variables**

If you want to enable automatic GitHub push features:

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your GitHub credentials:
```
USER_EMAIL_GITHUB=your_email@example.com
USERNAME_GITHUB=your_github_username
TOKEN_GITHUB=your_personal_access_token
REPO_GITHUB=your_repo_name
```

---

## 📊 Data Structure

Each CSV file in `Nepse_Data/` contains the following columns:

| Column | Description |
|--------|-------------|
| Date | Trading date |
| Open | Opening price |
| High | Highest price |
| Low | Lowest price |
| Close | Closing price |
| Volume | Trading volume |

---

## 🔧 Execution Guidelines

When running scripts:

1. **Execute from the parent directory** (one level above Nepal_Stock_Data folder)
2. Scripts will automatically detect if running in Google Colab or local environment
3. For Colab, scripts will clone the repository automatically if needed
4. Data is stored in `Nepse_Data/` by default

**Example:**
```
your_project/
├── Nepal_Stock_Data/        ← Execute scripts from here
├── nepse_data_update.py     ← or reference from parent
└── (other files)
```

---

## 📊 Example Use Cases

- 📈 Train LSTM/Transformer models on NEPSE time-series data
- 🔍 Analyze financial health by sector
- 📊 Create dashboards using Plotly, Seaborn
- 🎓 Conduct academic research in economics/finance
- 💹 Develop trading strategies
- 📉 Time-series forecasting

---

## 📋 Dataset Categories

**Nepse_Data/** contains data for the following sectors:

- Commercial Banks
- Corporate Debentures
- Development Bank Limited
- Finance
- Government Bonds
- Hotels and Tourism
- Hydro Power
- Investment
- Life Insurance
- Manufacturing and Processing
- Microfinance
- Mutual Funds
- Non-Life Insurance
- Others
- Preference Share
- Promoter Share
- Tradings

---

## 📄 Related Data Files

Located in `other_nepse_detail/`:

- **listed_company.csv**: Complete list of all companies traded on NEPSE with sectors
- **only_public_holidays.csv**: Public holidays only
- **public_and_weekly_holidays.csv**: All non-trading days (weekends + public holidays)
- **trading_calendar.csv**: Official trading calendar

---

## 📃 License & Usage Terms

You are free to use, modify, and share the datasets for **educational or non-commercial purposes**.

If you're from the original data sources and object to this usage, please contact:

📧 **Email:** sudipsudip5250@gmail.com

---

## Version

**v1.0** - Initial Release (February 2026)

I will remove the content immediately upon request.

**🙏 Acknowledgements**
Thanks to the owner of:
***Nepal Stock Exchange
sharesansar***
Their public data platforms made this project possible.

👤 Author
Sudip Bhattarai
GitHub: @sudipsudip5250

**📌 Final Note**
This is part of an open data initiative to promote:

📚 Financial literacy
💹 Stock market understanding
🤖 Machine learning in finance

The Interactive Python Notebook(ipynb) execution didn't face any problem with Google Colab so try it's when you face any problem with executing locally. Feel free to contribute and improve this project! 💡

Let me know if you'd have any question or any other problem/solution or new idea.


<p align="center"><strong> ***THANK YOU ***</strong></p>

