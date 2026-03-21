# Documentation

Setup and administration guides for the NEPSE Stock Data automation bot.

---

## 📚 Guides

### 🚀 [Quick Reference](./QUICK_REFERENCE.md)

Fast setup guide with copy-paste values, secrets configuration, and workflow schedules.

### 🔐 [Security Best Practices](./SECURITY.md)

Security guidelines, credential management, and protection strategies.

### 🧹 [Repository Maintenance](./MAINTENANCE.md)

How to clean up repository history and manage growth from frequent GitHub Actions commits.

---

---

## ⚡ Quick Start

1. **Add Repository Secrets** (Settings → Secrets and variables → Actions)
   - `USER_EMAIL_GITHUB` = `bot@nepal-stock-data.local`
   - `USERNAME_GITHUB` = `NepalStockData[bot]`

2. **Update Workflow Permissions** (Settings → Actions → General)
   - ✅ Workflow permissions: "Read and write permissions"
   - ✅ Allow GitHub Actions to create and approve pull requests

3. **Done!** ✅
   - Workflows will run on schedule automatically
   - NEPSE data will be updated daily
   - All commits signed by bot

---

## 🛠️ Local Development

To run scripts locally:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env

# 3. Add your GitHub token (optional, for local testing)
# Create at: https://github.com/settings/tokens (repo scope only)

# 4. Run a script
python nepse_data_update.py
```

2. Update: Repository Settings → Secrets and variables
3. Verify: Run "Validate Secrets" workflow
4. Test: Run one data workflow manually

**Time required**: 5 minutes

---

## 🔑 Essential Information

### Bot Identity

```
Username: NepalStockData[bot]
Email: bot@nepal-stock-data.local
Purpose: Automated NEPSE data scraping
```

### Required Secrets

```
USER_EMAIL_GITHUB = bot@nepal-stock-data.local
USERNAME_GITHUB = NepalStockData[bot]
REPO_GITHUB = Nepal_Stock_Data
GITHUB_TOKEN = (built-in, no setup)
```

### Workflow Schedules

```
NEPSE Data   → Daily at 12:15 UTC (6:00 PM NPT)
Companies    → Sundays at 13:15 UTC (7:00 PM NPT)
Holidays     → 1st at 12:00 UTC (5:30 PM NPT)
Cleanup      → 1st at 00:00 UTC (5:30 AM NPT)
```

---

## ✅ Setup Verification

After setup, verify everything works:

```bash
# 1. Check secrets are configured
# → Go to: Actions tab → Run "Validate Secrets" workflow

# 2. Run a data workflow manually
# → Go to: Actions → "Nepse Data Update" → Run workflow

# 3. Check bot commits appear
git log --author="NepalStockData" --oneline

# 4. Verify commit details
git log --author="NepalStockData" --pretty=fuller
```

---

## 📞 When to Read Which Guide

| Situation         | Read This                      | Time   |
| ----------------- | ------------------------------ | ------ |
| First-time setup  | QUICK_REFERENCE.md             | 5 min  |
| Configure bot     | GITHUB_BOT_SETUP.md            | 20 min |
| Workflow details  | WORKFLOW_SETUP.md              | 15 min |
| Security audit    | SECURITY.md                    | 30 min |
| Troubleshooting   | QUICK_REFERENCE.md → Error Fix | 10 min |
| Credentials issue | SECURITY.md → Token Management | 15 min |

---

## 🚀 Typical Workflow

### For Repository Maintainer

1. **Week 1**: Complete all documentation
2. **Month 1**: Run workflows daily, monitor logs
3. **Ongoing**: Monthly security audits
4. **Every 90 days**: Rotate credentials

### For Team Member

1. **Day 1**: Read QUICK_REFERENCE.md
2. **Day 2**: Configure secrets and test
3. **Week 1**: Familiarize with workflows
4. **Ongoing**: Monitor workflow status

---

## 🔍 Documentation Highlights

### In GITHUB_BOT_SETUP.md

- ✅ Bot identity explanation
- ✅ Environment variable setup
- ✅ Workflow integration details
- ✅ Security considerations
- ✅ Setup checklist
- ✅ Troubleshooting guide

### In WORKFLOW_SETUP.md

- ✅ All 5 workflows explained
- ✅ Schedule details (UTC & NPT)
- ✅ What each workflow updates
- ✅ Manual execution steps
- ✅ Commit examples
- ✅ Common issues & solutions

### In QUICK_REFERENCE.md

- ✅ Copy-paste secret values
- ✅ Exact secret names (case-sensitive)
- ✅ Workflow schedules table
- ✅ Key file locations
- ✅ Common tasks with steps
- ✅ Do's and Don'ts table
- ✅ Error quick fix table

### In SECURITY.md

- ✅ Never do this (bad practices)
- ✅ Always do this (best practices)
- ✅ Token management strategies
- ✅ File security guidelines
- ✅ Credential compromise response
- ✅ Complete security checklist

---

## 📝 File Locations

### Configuration Files

```
.env.example              ← Template (safe, no secrets)
.env                      ← Local config (never commit)
.gitignore               ← Should include .env entry
```

### Workflow Files

```
.github/workflows/
├── Nepse_Data_Update.yml
├── Listed_Company_Update.yml
├── Holiday_Calendar_Update.yml
├── cleanup-workflow-logs.yml
└── check_secrets.yml
```

### Documentation

```
docs/
├── README.md             (This file)
├── QUICK_REFERENCE.md
├── GITHUB_BOT_SETUP.md
├── WORKFLOW_SETUP.md
└── SECURITY.md
```

---

## 🆘 Common Questions

### Q: Where do I configure secrets?

**A:** Repository → Settings → Secrets and variables → Actions

### Q: What's the bot username?

**A:** `NepalStockData[bot]` (include the [bot] suffix)

### Q: What's the bot email?

**A:** `bot@nepal-stock-data.local` (local domain, not a real email)

### Q: Should I use my personal token?

**A:** No. GitHub Actions provides `GITHUB_TOKEN` automatically.

### Q: Can I change the schedule?

**A:** Yes, edit `.github/workflows/*.yml` and modify the cron expression

### Q: How do I troubleshoot?

**A:** See [QUICK_REFERENCE.md - Error Quick Fix](./QUICK_REFERENCE.md#error-quick-fix)

### Q: Is my data secure?

**A:** Yes. See [SECURITY.md](./SECURITY.md) for complete details

---

## 🎓 Learning Path

**Beginner (Just want to use it)**

1. QUICK_REFERENCE.md - Quickstart
2. QUICK_REFERENCE.md - Common Tasks
3. Done! (5-10 minutes)

**Intermediate (Want to understand it)**

1. QUICK_REFERENCE.md - Complete
2. WORKFLOW_SETUP.md - Overview
3. GITHUB_BOT_SETUP.md - Configuration
4. Done! (30 minutes)

**Advanced (Want to manage it securely)**

1. All of Intermediate
2. SECURITY.md - Complete
3. Review all checklists
4. Done! (1-2 hours)

**Expert (Want to contribute)**

1. All of Advanced
2. Review all Python scripts
3. Review all workflow files
4. Review commit history
5. Document any custom changes

---

## 📊 Last Updated

- **Date**: March 21, 2026
- **Bot Version**: 1.0
- **Documentation Version**: 1.0
- **Status**: ✅ Production Ready

---

## 🔗 External Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Managing Secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Using GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Cron Syntax Reference](https://crontab.guru/)

---

## 📞 Need More Help?

1. **Review the relevant guide** above
2. **Check the troubleshooting section** in that guide
3. **Run "Validate Secrets"** workflow to check configuration
4. **Review workflow logs** for specific errors
5. **Test locally** with `.env` file before troubleshooting workflows

---

**Happy automating! 🚀**
