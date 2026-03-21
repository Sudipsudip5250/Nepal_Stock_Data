# Security Best Practices

Protecting credentials and following security best practices.

---

## 🔐 Protecting Credentials

### ❌ Never:

```python
# Hardcode credentials in code
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxx"
GITHUB_USER = "username"
```

```yaml
# Put secrets in workflow files
env:
  TOKEN: "ghp_xxxxxxxxxxxxxxxxxxx"
```

```bash
# Commit .env file
git add .env
git commit -m "Add .env"
```

### ✅ Always:

```python
# Use environment variables from .env
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN_GITHUB")
user = os.getenv("USERNAME_GITHUB")
```

```yaml
# Use GitHub secrets in workflows
env:
  TOKEN_GITHUB: ${{ secrets.GITHUB_TOKEN }}
  USERNAME_GITHUB: ${{ secrets.USERNAME_GITHUB }}
  USER_EMAIL_GITHUB: ${{ secrets.USER_EMAIL_GITHUB }}
```

```bash
# Add .env to .gitignore
echo '.env' >> .gitignore
```

---

## 🔑 Security Checklist

- [ ] `.env` is in `.gitignore` (never commit)
- [ ] Secrets are in repository settings (not in code)
- [ ] Using `GITHUB_TOKEN` (auto-generated, safe)
- [ ] Using bot credentials consistently
- [ ] Workflow logs checked for errors
- [ ] No hardcoded tokens in scripts
- [ ] `.env.example` has no real values

---

## 🔗 Related Documentation

- [Quick Reference](./QUICK_REFERENCE.md)
- ✅ Bot should NOT delete branches
- ✅ Bot should NOT modify workflows

**Implementation:**

```yaml
# In workflow - only necessary permissions
permissions:
  contents: write # Can commit
  # contents: read (sufficient for most operations)
  # No admin access
  # No workflow permissions
```

---

## 🔐 Secret Management Best Practices

### Creating Secrets

**Path:** Repository → Settings → Secrets and variables → Actions

```
Name: USER_EMAIL_GITHUB
Value: bot@nepal-stock-data.local
Environment: (leave blank for all)
```

### Viewing Secrets

⚠️ **Important:**

- Once created, secrets cannot be viewed again
- Only their name appears in settings
- This is intentional for security

### Rotating Secrets

Every 90 days:

```
1. Create new secret with different value
2. Update workflow to use new secret name
3. Delete old secret
4. Monitor for any failures
```

### Secret Scope

```yaml
# ✅ Correct - Secrets scoped to specific workflow
env:
  TOKEN: ${{ secrets.GITHUB_TOKEN }} # Only visible in this job

# ❌ Wrong - Secrets exposed to all jobs
jobs:
  all-jobs-see-secrets:
    env:
      TOKEN: ${{ secrets.GITHUB_TOKEN }} # Too broad
```

---

## 📋 Branch Protection

### For Automated Bot Commits

Allow exceptions for bot:

**Path:** Settings → Branches → Branch protection rules → main

```
Rule: Require pull request reviews
Exception: NepalStockData[bot]  # Allow bot to push directly

Rule: Dismiss stale pull request approvals
Exception: NepalStockData[bot]

Rule: Require status checks to pass
Exception: NepalStockData[bot] (optional, for speed)
```

---

## 🚨 Incident Response

### If Credentials Are Compromised

1. **Immediate Action (< 5 minutes):**

   ```bash
   # Delete compromised token from GitHub
   # This expires it immediately
   # No action needed in code yet
   ```

2. **Short Term (< 1 hour):**

   ```bash
   # Create new token with limited scope
   # Update repository secrets
   # Monitor for unusual activity
   ```

3. **Medium Term (< 1 day):**

   ```bash
   # Review commit history for suspicious changes
   git log --since="6 hours ago"

   # Check for pushed code
   git log --author="NepalStockData[bot]" --since="6 hours ago"
   ```

4. **Long Term (< 1 week):**

   ```bash
   # If token was in code, remove from history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty --tag-name-filter cat -- --all

   # Force push to remove from GitHub
   # (Only if collaboration hasn't started)
   ```

---

## ✅ Security Checklist

**Initial Setup:**

- [ ] Create `.gitignore` with `.env` entry
- [ ] Create `.env.example` (template only)
- [ ] Add secrets via GitHub Settings (never in code)
- [ ] Review secret names for typos
- [ ] Set repository permissions to "Read and write"
- [ ] Configure branch protection rules

**Ongoing:**

- [ ] Never commit `.env` file
- [ ] Rotate tokens every 90 days
- [ ] Monitor commit history for anomalies
- [ ] Review workflow logs regularly
- [ ] Audit repository secrets monthly
- [ ] Update bot credentials if needed
- [ ] Check for exposed credentials
- [ ] Remove old/unused tokens

**Before Deployment:**

- [ ] All secrets are configured
- [ ] Workflow permissions are correct
- [ ] Branch protection is set up
- [ ] No credentials in code
- [ ] Test with limited token scope
- [ ] Verify bot email format
- [ ] Check bot username format
- [ ] Review security policy

---

## 🔗 Related Resources

- [GitHub Security Best Practices](https://docs.github.com/en/actions/security-guides)
- [Managing Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Using GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- [Keeping Actions Up to Date](https://docs.github.com/en/actions/security-guides/dependabot-and-dependabot-actions)

---

## 📞 Security Incident Reporting

If you discover a security issue:

1. **Do NOT create a public GitHub issue**
2. **Email security team immediately**
3. **Include affected files and timeline**
4. **Keep details confidential until patch**

---

**Last Updated**: March 21, 2026  
**Security Level**: ⭐⭐⭐⭐⭐ (Recommended for Production)
