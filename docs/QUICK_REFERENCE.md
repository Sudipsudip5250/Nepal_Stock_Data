# Quick Reference Guide

Copy-paste setup guide for NEPSE data automation.

---

## ⚡ Setup in 3 Steps

### Step 1: Add Repository Secrets

**Path**: Settings → Secrets and variables → Actions → New repository secret

```
Name: USER_EMAIL_GITHUB
Value: bot@nepal-stock-data.local

Name: USERNAME_GITHUB
Value: NepalStockData[bot]
```

### Step 2: Configure .env (for local testing)

Copy `.env.example` to `.env` and fill in:

```env
USER_EMAIL_GITHUB=bot@nepal-stock-data.local
USERNAME_GITHUB=NepalStockData[bot]
TOKEN_GITHUB=
```

### Step 3: Update Workflow Permissions

**Path**: Settings → Actions → General

```
✅ Read and write permissions
✅ Allow GitHub Actions to create and approve pull requests
```

---

## 📅 Automated Schedules

| Task       | Time (UTC) | Time (NPT) | Frequency |
| ---------- | ---------- | ---------- | --------- |
| NEPSE Data | 12:15      | 6:00 PM    | Daily     |
| Companies  | 13:15      | 7:00 PM    | Sundays   |
| Holidays   | 14:15      | 8:00 PM    | Monthly   |

---

## 🤖 Bot Information

```
Username: NepalStockData[bot]
Email: bot@nepal-stock-data.local
```

---

## 🔗 Related Documentation

- [Security Best Practices](./SECURITY.md)
