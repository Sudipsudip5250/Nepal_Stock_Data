# Repository Maintenance & Cleanup

Guide for cleaning up repository history when it grows too large due to frequent GitHub Actions commits.

---

## 🔍 Why Repository Cleanup?

### The Problem

GitHub Actions commits frequently with daily data updates:

- **Daily NEPSE updates** = ~1-14 commit/day
- **Weekly company updates** = ~1 commit/week
- **Monthly holiday updates** = ~1 commit/month
- **Result**: ~4000+ commits per year

Each commit adds to repository size:

```
commits × average file changes = repository size
4000 commits × 500+ CSV files ≈ repository bloat
```

### Impact

- ❌ Slower cloning: `git clone` takes longer
- ❌ Slower pulling: `git pull` takes longer
- ❌ Slower pushing: `git push` takes longer
- ❌ Wasted storage: Unnecessary history stored
- ❌ More bandwidth: More data to transfer

### Solution

Reset repository history while keeping current data. Every ~6 months or when size exceeds 500MB.

---

## 📋 When to Cleanup

**Signs you need cleanup:**

```bash
# Check repository size
du -sh .git

# If size > 500MB, time to cleanup
# Or if cloning takes > 5 minutes
```

**Recommended schedule:**

- ✅ Every 6 months (quarterly cleanup)
- ✅ When repository exceeds 500MB
- ✅ When cloning/pulling becomes slow

---

## 🧹 Cleanup Process

### Step 1: Create Orphan Branch

Creates a new branch with no history:

```bash
# Switch to new orphan branch
git checkout --orphan temp-branch

# This branch contains all current files but no history
# Status shows all files as "new file"
git status
```

### Step 2: Add All Current Files

```bash
# Stage all files
git add .

# Verify files are staged
git status
```

### Step 3: Create Clean Commit

Commit with version number and data date:

```bash
# Commit with meaningful message
git commit -m "V1.0.0 release with upto ....... data"

# This is the new "first commit" with all current data
```

### Step 4: Delete Old Main Branch

```bash
# Delete old main branch locally
git branch -D main

# This removes the old history locally
# The old commits are still safe in the remote
```

### Step 5: Rename Branch to Main

```bash
# Rename temp-branch to main
git branch -m main

# Verify you're on main
git branch
```

### Step 6: Force Push to Remote

⚠️ **Warning: This rewrites repository history!**

```bash
# Force push main branch to remote
git push origin main --force

# This replaces remote history with new clean history
```

### Step 7: Cleanup Remote (Optional)

If temp-branch was pushed to remote:

```bash
# Delete remote temp-branch if it exists
git push origin --delete temp-branch

# (May error if branch doesn't exist - that's OK)
```

---

## 📊 Before & After

### Before Cleanup

```
.git/ = 800 MB+
commits = 12000+
history = 3 years of daily updates
clone time = 10+ minutes
```

### After Cleanup

```
.git/ = 50 MB
commits = 1 (initial)
history = reset
clone time = < 1 minute
```

---

## ⚠️ Important Warnings

### ❌ What This Does

```
✅ Keeps all current data files
❌ Deletes all commit history
❌ Removes git blame information
❌ Makes old commits unreachable
```

### ⚠️ Consequences

- **Users with clones must re-clone** after force push
- **Collaborators might have merge conflicts** if they have uncommitted changes
- **GitHub Actions logs** are still available (different from git history)
- **You lose commit history** (but this is OK for data repository)

### ✅ Safe to Do Because

- ✅ You're not deleting data, only history
- ✅ All current files are preserved
- ✅ It's a data repository (not code repository)
- ✅ Workflows generate new commits naturally
- ✅ History isn't important for stock data

---

## 📋 Complete Cleanup Script

Copy-paste ready script:

```bash
#!/bin/bash
# Repository cleanup script

echo "🧹 Starting repository cleanup..."

# 1. Create orphan branch
echo "1️⃣ Creating orphan branch..."
git checkout --orphan temp-branch

# 2. Add all files
echo "2️⃣ Staging all files..."
git add .

# 3. Commit
echo "3️⃣ Creating clean commit..."
git commit -m "V1.0.0 release with upto $(date +%Y-%m-%d) data"

# 4. Delete old main
echo "4️⃣ Deleting old main branch..."
git branch -D main

# 5. Rename temp-branch
echo "5️⃣ Renaming branch to main..."
git branch -m main

# 6. Force push
echo "6️⃣ Pushing to remote..."
git push origin main --force

# 7. Cleanup remote
echo "7️⃣ Cleaning up remote branches..."
git push origin --delete temp-branch 2>/dev/null || true

echo "✅ Cleanup complete!"
echo "📊 New repository size:"
du -sh .git
```

**Save as:** `cleanup-repo.sh`

**Run:** `bash cleanup-repo.sh`

---

## 🔔 Notifying Users

After cleanup, inform users:

````markdown
## ⚠️ Repository Restructured

Repository history was reset on [DATE] to improve performance.

**Action Required:**

```bash
# If you have a clone, you must re-clone:
git clone https://github.com/NepalStockData/Nepal_Stock_Data.git
```
````

**What Changed:**

- ✅ All current data preserved
- ❌ Git history reset (started fresh)
- ✅ Repository size reduced from XMB to YMB
- ✅ Clone/pull now ~10x faster

**If you have uncommitted changes:**

```bash
# Save your changes
git stash

# Re-clone the repository
git clone https://github.com/NepalStockData/Nepal_Stock_Data.git

# Restore your changes if needed
git stash pop
```

````

---

## 🔒 Safety Precautions

### Before Cleanup

**Backup current state:**

```bash
# Create backup tag
git tag -a backup-before-cleanup-$(date +%Y-%m-%d) main -m "Backup before cleanup"

# Push backup tag to remote
git push origin backup-before-cleanup-$(date +%Y-%m-%d)
````

**Verify current data:**

```bash
# Check file count
find Nepse_Data -type f | wc -l

# Check directory size
du -sh Nepse_Data/
du -sh other_nepse_detail/
```

### After Cleanup

**Verify cleanup:**

```bash
# Check new repository size
du -sh .git

# Verify main data exists
ls -la Nepse_Data/Commercial_Banks/

# Check commit count
git log --oneline | wc -l

# Should be 1
```

---

## 🆘 Troubleshooting

### Error: "failed to push some refs"

**Cause:** Remote refs don't match local

**Solution:**

```bash
# Check remote status
git remote -v

# Verify you're on main
git branch

# Force push again
git push origin main --force
```

### Error: "src refspec main does not match any"

**Cause:** Branch wasn't renamed properly

**Solution:**

```bash
# Check what branch you're on
git branch

# Rename to main if needed
git branch -m main

# Try pushing again
git push origin main --force
```

### Collaborators can't pull after cleanup

**Solution (for collaborators):**

```bash
# Back up any local changes
git stash

# Remove local branch
git branch -D main

# Fetch updated main from remote
git fetch origin

# Track remote main
git checkout -b main origin/main

# Restore stashed changes if needed
git stash pop
```

---

## 📅 Maintenance Schedule

### Monthly (Automated)

- GitHub Actions run workflows
- Commits created automatically
- Repository grows slightly

### Quarterly (Manual - Every 3 Months)

- Monitor repository size
- Check if cleanup needed
- Document maintenance

### Semi-Annually (Cleanup - Every 6 Months)

- Run cleanup process
- Notify users
- Create backup tag
- Create release note

**Cleanup Dates:**

- Spring: March
- Fall: September

---

## 📝 Cleanup Checklist

Before cleanup:

- [ ] All data files are up-to-date
- [ ] GitHub Actions workflows are working
- [ ] No uncommitted changes
- [ ] Backup tag created
- [ ] Users notified

During cleanup:

- [ ] Orphan branch created
- [ ] All files staged
- [ ] Meaningful commit message
- [ ] Old main branch deleted
- [ ] Branch renamed to main
- [ ] Force pushed to remote

After cleanup:

- [ ] Repository size verified (< 200MB)
- [ ] Clone/pull tested
- [ ] Data files verified
- [ ] Commit count verified (should be 1)
- [ ] Release notes updated
- [ ] Users informed

---

## 🔗 Related Documentation

- [Quick Reference](./QUICK_REFERENCE.md)
- [Security Best Practices](./SECURITY.md)

---

## 💡 Additional Tips

### Monitor Repository Size

```bash
# Monitor .git folder size
watch -n 60 'du -sh .git'

# Export size stats
du -sh .git > git-size-$(date +%Y-%m-%d).txt
```

### Automate Cleanup Reminder

Add to your calendar or workflow:

```yaml
# .github/workflows/repo-size-check.yml
name: Repository Size Check
on:
  schedule:
    - cron: "0 0 1 * *" # Monthly on 1st

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check repo size
        run: |
          SIZE=$(du -sh .git | cut -f1)
          echo "Repository size: $SIZE"
```

### Detailed Git Log Before Cleanup

Before deleting history, save it:

```bash
# Export full log with diffs
git log --all --stat > git-history-backup-$(date +%Y-%m-%d).txt

# Export as JSON
git log --all --format="%H %aI %s" > git-commits-$(date +%Y-%m-%d).json
```

---

**Last Updated:** March 21, 2026  
**Version:** 1.0
