# GitHub API Logger - Quick Start

**Problem Solved:** Streamlit Cloud can't write to GitHub files → Use GitHub API to write to separate branch!

---

## Why This is Better Than Google Sheets:

| Feature | GitHub API | Google Sheets |
|---------|------------|---------------|
| Setup | 15 min | 30 min |
| External accounts | None (already have GitHub) | Need GCP |
| Data location | Your repo | Google servers |
| Backup | Automatic (Git history) | Manual export |
| Cost | Free forever | Free (with limits) |

---

## Quick Setup (3 Steps)

### 1️⃣ Create GitHub Token (5 min)

```
GitHub Profile → Settings → Developer Settings
→ Personal Access Tokens → Tokens (classic)
→ Generate new token
  ✅ Select: repo scope
  📋 Copy token (ghp_...)
```

### 2️⃣ Create Data Branch (2 min)

```bash
git checkout --orphan data
git rm -rf .
echo "# Study Data" > README.md
git add README.md
git commit -m "Initialize data branch"
git push origin data
git checkout main
```

### 3️⃣ Add to Streamlit Secrets (5 min each app)

Go to: https://share.streamlit.io/ → Your App → Settings → Secrets

```toml
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
GITHUB_REPO = "tylertgb/mphil_thesis_project"
```

**Repeat for all 3 apps** ✅✅✅

---

## Test It

1. Push code:
   ```bash
   git add .
   git commit -m "Add GitHub API logger"
   git push origin main
   ```

2. Wait 2 min for redeploy

3. Complete test response on deployed app

4. Check data branch:
   ```bash
   git fetch origin data
   git checkout data
   cat study_data/demographics.csv
   ```

✅ Your data is there!

---

## Retrieve Data Anytime

```bash
# Fetch latest data from cloud
git fetch origin data
git checkout data

# Copy to main branch
git checkout main
git checkout data -- study_data/
```

Or download from GitHub web interface:
- Switch to **data** branch
- Browse `study_data/` folder
- Download CSV files

---

## How It Avoids App Restarts

```
main branch = code
  ↓ changes trigger restart

data branch = data only  
  ↓ changes do NOT trigger restart ✅
```

**Smart!** 🧠

---

## Session Persistence Fix

The GitHub logger also solves cross-app session tracking:

```python
# Variant A writes: "P001 completed variant_a"
logger.github_logger.log_session("P001", "variant_a", "completed")

# Variant B reads: "Check if P001 has variant_a completed"
# Fetches from data branch → ✅ Yes, let them continue
```

No more "No active session found" errors!

---

## Troubleshooting

**"Authentication failed"**
→ Check token in Streamlit secrets

**"Data not syncing"**
→ Check Streamlit Cloud logs (Settings → Logs)

**"Branch not found"**
→ Create data branch (Step 2)

---

## Full Guide

See **GITHUB_API_SETUP.md** for detailed instructions

---

**Ready to deploy?** Push the changes and add your secrets! 🚀
