# GitHub Actions Workflows

Automated workflow definitions for NEPSE data scraping and repository management.

---

## 📂 Workflow Files

```
.github/workflows/
├── Nepse_Data_Update.yml              ← Daily stock data scraping
├── Listed_Company_Update.yml          ← Weekly company list update
├── Holiday_Calendar_Update.yml        ← Monthly holiday calendar
├── cleanup-workflow-logs.yml          ← Monthly log cleanup
├── check_secrets.yml                  ← Secret validation (manual)
└── README.md                          ← This file
```

---

## 🔄 Workflow Descriptions

### 1. Nepse Data Update

**File**: `Nepse_Data_Update.yml`

**Purpose**: Automatically scrape and update latest NEPSE stock market data

**Schedule**:

- Daily at **12:15 UTC** (6:00 PM NPT)
- Manual trigger available

**What it does**:

1. Checks if today is a trading day
2. Skips Friday, Saturday, and public holidays
3. Downloads latest market data
4. Updates CSV files in `Nepse_Data/*/` folders
5. Auto-commits changes with bot signature

**Git Config**:

```yaml
git config --global user.email "bot@nepal-stock-data.local"
git config --global user.name "NepalStockData[bot]"
```

**Files Modified**:

```
Nepse_Data/
├── Commercial_Banks/*.csv
├── Development_Bank_Limited/*.csv
├── Finance/*.csv
├── Government_Bonds/*.csv
├── Hydro_Power/*.csv
├── Investment/*.csv
├── Life_Insurance/*.csv
├── Manufacturing_And_Processing/*.csv
├── Microfinance/*.csv
├── Mutual_Fund/*.csv
├── Non-Life_Insurance/*.csv
├── Others/*.csv
├── Preference_Share/*.csv
├── Promoter_Share/*.csv
└── Tradings/*.csv
```

**Required Secrets**:

- `GITHUB_TOKEN` (built-in)
- `USER_EMAIL_GITHUB`
- `USERNAME_GITHUB`
- `REPO_GITHUB`

---

### 2. Listed Company Update

**File**: `Listed_Company_Update.yml`

**Purpose**: Update the list of companies currently listed on NEPSE

**Schedule**:

- Every **Sunday at 13:15 UTC** (7:00 PM NPT)
- Manual trigger available

**What it does**:

1. Scrapes current list of NEPSE-listed companies
2. Compares with existing data
3. Only commits if changes detected
4. Auto-commits with bot signature

**Git Config**:

```yaml
git config --global user.email "bot@nepal-stock-data.local"
git config --global user.name "NepalStockData[bot]"
```

**Files Modified**:

```
other_nepse_detail/
└── listed_company.csv
```

**Required Secrets**:

- `GITHUB_TOKEN` (built-in)
- `USER_EMAIL_GITHUB`
- `USERNAME_GITHUB`
- `REPO_GITHUB`

---

### 3. Holiday Calendar Update

**File**: `Holiday_Calendar_Update.yml`

**Purpose**: Update trading holidays and generate calendar formats

**Schedule**:

- 1st of each month at **12:00 UTC** (5:30 PM NPT)
- Manual trigger available

**What it does**:

1. Adds weekends (Friday & Saturday) to calendar
2. Scrapes public holidays from NEPSE
3. Fills missing months with data
4. Generates multiple calendar formats
5. Auto-commits only if changes detected

**Git Config**:

```yaml
git config --global user.email "bot@nepal-stock-data.local"
git config --global user.name "NepalStockData[bot]"
```

**Files Modified**:

```
other_nepse_detail/
├── trading_calendar.csv
├── only_public_holidays.csv
└── public_and_weekly_holidays.csv
```

**Required Secrets**:

- `GITHUB_TOKEN` (built-in)
- `USER_EMAIL_GITHUB`
- `USERNAME_GITHUB`
- `REPO_GITHUB`

---

### 4. Cleanup Workflow Logs

**File**: `cleanup-workflow-logs.yml`

**Purpose**: Housekeeping - delete old workflow run logs to save storage

**Schedule**:

- 1st of each month at **00:00 UTC** (5:30 AM NPT)
- Manual trigger available

**What it does**:

1. Lists all workflow runs
2. Identifies runs older than the latest 5
3. Deletes old runs
4. Frees up GitHub Actions storage

**Note**: This doesn't affect data workflows or commit history

---

### 5. Validate Secrets

**File**: `check_secrets.yml`

**Purpose**: Verify that all required secrets are configured

**Trigger**: Manual only (via `workflow_dispatch`)

**What it does**:

1. Displays which secrets are set
2. Shows masked values (for security)
3. Helps troubleshoot missing credentials
4. Confirms configuration is correct

**How to run**:

```
Go to: Actions tab → "Validate Secrets" → "Run workflow"
```

---

## 🔐 Bot Configuration

### Git Identity (Used in All Data Workflows)

```bash
User Name:  NepalStockData[bot]
User Email: bot@nepal-stock-data.local
```

This ensures all automated commits are:

- ✅ Clearly identified as bot-generated
- ✅ Traceable in commit history
- ✅ Professional and organized
- ✅ Easy to filter in logs

### Example Commit

```
commit a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Author: NepalStockData[bot] <bot@nepal-stock-data.local>
Date:   Fri Mar 21 18:15:00 2026 +0000

    📊 Update NEPSE data via GitHub Actions

    Automated daily scrape of stock market data
    - Updated all sector CSV files
    - No errors detected
```

---

## 📋 Environment Variables

### Required in Repository Secrets

**Where to set**: Repository → Settings → Secrets and variables → Actions

| Secret              | Value                        | Purpose                    |
| ------------------- | ---------------------------- | -------------------------- |
| `USER_EMAIL_GITHUB` | `bot@nepal-stock-data.local` | Bot email for commits      |
| `USERNAME_GITHUB`   | `NepalStockData[bot]`        | Bot username in commits    |
| `REPO_GITHUB`       | `Nepal_Stock_Data`           | Repository name for URLs   |
| `GITHUB_TOKEN`      | (built-in)                   | GitHub auto-provided token |

### Loaded in Workflows

All workflows use these secrets via `${{ secrets.NAME }}` syntax:

```yaml
env:
  USER_EMAIL_GITHUB: ${{ secrets.USER_EMAIL_GITHUB }}
  USERNAME_GITHUB: ${{ secrets.USERNAME_GITHUB }}
  TOKEN_GITHUB: ${{ secrets.GITHUB_TOKEN }}
  REPO_GITHUB: ${{ secrets.REPO_GITHUB }}
```

---

## 🚀 How to Run Workflows

### Manually Trigger a Workflow

1. Go to **Actions** tab in GitHub repository
2. Click the workflow name (e.g., "Nepse Data Update")
3. Click **Run workflow** button
4. Select **main** branch
5. Click green **Run workflow** button
6. Monitor the logs in real-time

### View Workflow Logs

1. Go to **Actions** tab
2. Click the workflow run
3. Click the job name
4. Expand individual steps to see logs

### Check Workflow Status

1. Go to **Actions** tab
2. Green checkmark = successful
3. Red X = failed
4. Yellow circle = running

---

## ⏰ Schedule Reference

### UTC Times

| Workflow   | Frequency    | Time      |
| ---------- | ------------ | --------- |
| NEPSE Data | Daily        | 12:15 UTC |
| Companies  | Sundays      | 13:15 UTC |
| Holidays   | 1st of month | 12:00 UTC |
| Cleanup    | 1st of month | 00:00 UTC |

### Nepal Time (NPT = UTC + 5:45)

| Workflow   | Frequency    | Time    |
| ---------- | ------------ | ------- |
| NEPSE Data | Daily        | 6:00 PM |
| Companies  | Sundays      | 7:00 PM |
| Holidays   | 1st of month | 5:30 PM |
| Cleanup    | 1st of month | 5:30 AM |

### Cron Expression Format

```yaml
# Cron: minute hour day month weekday
# Examples:
'15 12 * * *'   = 12:15 UTC daily
'15 13 * * 0'   = 13:15 UTC Sundays
'0 12 1 * *'    = 12:00 UTC on 1st
'0 0 1 * *'     = 00:00 UTC on 1st
```

---

## 🔧 Modifying Workflows

### Change Schedule

Edit the cron expression in the workflow file:

```yaml
on:
  schedule:
    - cron: "15 12 * * *" # Change this line
```

Use [crontab.guru](https://crontab.guru/) to test cron syntax

### Change Commit Message

Edit the git commit command:

```yaml
git commit -m "📊 Update NEPSE data via GitHub Actions"
```

### Add New Workflow

1. Copy existing workflow file
2. Rename to descriptive name
3. Update schedule and script names
4. Push to `.github/workflows/`
5. Test manually before relying on schedule

---

## 🐛 Troubleshooting

### Workflow Not Running on Schedule

**Possible Causes:**

- Workflow is disabled
- Branch protection rules blocking commits
- Schedule is incorrect
- Repository inactive

**Solutions:**

1. Actions → Workflow → Check enabled status
2. Settings → Branches → Check protection rules
3. Verify cron expression on [crontab.guru](https://crontab.guru/)
4. Push a commit to wake up the repository

### Workflow Fails Immediately

**Possible Causes:**

- Missing secrets
- Incorrect secret names
- Permission issues

**Solutions:**

1. Run "Validate Secrets" workflow
2. Check secret names (case-sensitive)
3. Verify workflow permissions: Settings → Actions → "Read and write"

### No Commits After Workflow Runs

**Possible Causes:**

- No data changed (workflow skips empty commits)
- Branch protection preventing push
- Bot doesn't have write access

**Solutions:**

1. Check workflow logs for "No changes to commit"
2. Review branch protection rules
3. Ensure bot is exception to protection rules

---

## 📊 Workflow Metrics

### Typical Run Times

```
Nepse Data Update: 5-15 minutes
Listed Company: 3-8 minutes
Holiday Calendar: 2-5 minutes
Cleanup Logs: 1-2 minutes
Validate Secrets: < 30 seconds
```

### Data Volume

```
Total CSV files: 100+
Update frequency: Daily + Weekly + Monthly
Commit size: 10-50 KB per run
```

---

## 🔗 Related Documentation

- [Bot Setup Guide](../docs/GITHUB_BOT_SETUP.md)
- [Workflow Setup Guide](../docs/WORKFLOW_SETUP.md)
- [Security Best Practices](../docs/SECURITY.md)
- [Quick Reference](../docs/QUICK_REFERENCE.md)

---

## ✅ Verification Checklist

Before deploying to production:

- [ ] All secrets configured in repository
- [ ] Workflow permissions set to "Read and write"
- [ ] All workflows enabled
- [ ] Test each workflow manually
- [ ] Verify bot commits appear correctly
- [ ] Check commit author is `NepalStockData[bot]`
- [ ] Verify email is `bot@nepal-stock-data.local`
- [ ] Monitor first few automated runs
- [ ] Confirm schedules match timezone

---

**Last Updated**: March 21, 2026  
**Workflow Version**: 1.0  
**Status**: ✅ Ready for Production
