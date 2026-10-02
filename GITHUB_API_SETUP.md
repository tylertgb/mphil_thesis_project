# GitHub API Data Collection Setup

## Overview

Instead of Google Sheets or external databases, we write data directly to GitHub using its REST API. This avoids Streamlit Cloud app restarts by using a **separate `data` branch**.

### Why This Works:
✅ **No external services** - Everything stays in your GitHub repo  
✅ **No app restarts** - Data branch separate from code (main branch)  
✅ **Free forever** - GitHub's built-in API  
✅ **Easy retrieval** - Just `git pull` from data branch  
✅ **Version controlled** - All data changes tracked  

---

## Setup (15 minutes)

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub → **Settings** (your profile, top right)
2. Scroll down → **Developer settings** (left sidebar)
3. **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token (classic)**
5. Settings:
   - **Note:** `streamlit-data-logger`
   - **Expiration:** 90 days (or No expiration for thesis duration)
   - **Scopes:** Check only `repo` (full repository access)
6. Click **Generate token**
7. **Copy the token immediately!** (starts with `ghp_`)

⚠️ **Save this token securely - you can't see it again!**

---

### Step 2: Create Data Branch (Local)

```bash
# Create and push empty data branch
git checkout --orphan data
git rm -rf .
echo "# Study Data Branch" > README.md
git add README.md
git commit -m "Initialize data branch"
git push origin data

# Switch back to main
git checkout main
```

**What this does:**
- Creates isolated branch for data
- Main branch = code (triggers app restarts when changed)
- Data branch = data only (no restarts)

---

### Step 3: Configure Streamlit Cloud Secrets

For **each of your 3 deployed apps**:

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Select app (e.g., **mphil-study-variant-a**)
3. **Settings** → **Secrets**
4. Add:

```toml
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
GITHUB_REPO = "tylertgb/mphil_thesis_project"
```

5. Click **Save**
6. **Repeat for all 3 apps**

---

### Step 4: Update requirements.txt

Add `requests` library (already done):

```txt
requests>=2.31.0
```

---

### Step 5: Deploy & Test

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Add GitHub API logger"
   git push origin main
   ```

2. Wait for Streamlit Cloud to redeploy (~2 min)

3. Open deployed app

4. Complete test response

5. Check data branch:
   ```bash
   git fetch origin data
   git checkout data
   ls study_data/
   ```

You should see CSV files with your test data!

---

## How It Works

```
Participant fills form
    ↓
App calls DualLogger
    ↓
DualLogger writes to:
  1. Local CSV (immediate backup)
  2. GitHub API → 'data' branch
    ↓
Streamlit Cloud sees:
  - main branch unchanged ✅ (no restart)
  - data branch updated ✅ (data saved)
```

---

## Retrieving Your Data

### Option A: Pull Data Branch

```bash
# Fetch latest data
git fetch origin data
git checkout data

# Data is in study_data/*.csv
ls study_data/

# Merge into main if needed
git checkout main
git checkout data -- study_data/
git add study_data/
git commit -m "Update study data"
```

### Option B: Download from GitHub UI

1. Go to your repo on GitHub
2. Switch branch dropdown → select **data**
3. Navigate to `study_data/`
4. Click on a CSV file → **Raw** → **Save as**

### Option C: Automated Script

```python
# download_data.py
import subprocess

subprocess.run(["git", "fetch", "origin", "data"])
subprocess.run(["git", "checkout", "data", "--", "study_data/"])
print("✅ Data downloaded to study_data/")
```

---

## Session Persistence Across Apps

The GitHub logger includes `log_session()` for tracking active sessions:

```python
# In Variant A app (when participant completes)
logger.github_logger.log_session(participant_id, "variant_a", "completed")

# In Variant B app (check if A was completed)
# Fetch active_sessions.csv from data branch
# Check if participant_id has variant_a status=completed
```

This solves the "No active session found" issue!

---

## Troubleshooting

### "Authentication failed"
- Check token is correct in Streamlit secrets
- Ensure token has `repo` scope
- Token might have expired (regenerate)

### "Resource not accessible by personal access token"
- Token needs `repo` scope (not just `public_repo`)
- Recreate token with correct permissions

### "Reference does not exist"
- Data branch not created yet
- Run Step 2 commands to create it

### Data not appearing
- Check Streamlit Cloud logs (Settings → Logs)
- Look for error messages from GitHub API
- Verify `GITHUB_REPO` format: `username/repo_name`

### Still writing to local CSV only
- Secrets not configured in Streamlit Cloud
- Check for typos in secret names
- Redeploy app after adding secrets

---

## Security Best Practices

⚠️ **Keep secret:**
- GitHub Personal Access Token
- Never commit tokens to code

✅ **Safe to share:**
- Data branch contents (research data)
- Repo link (public repos)

🔄 **Token management:**
- Set expiration dates
- Revoke old tokens
- Use separate tokens for different projects

---

## Advantages Over Google Sheets

| Feature | GitHub API | Google Sheets |
|---------|-----------|---------------|
| Setup time | 15 min | 30 min |
| External dependencies | None | GCP account |
| Data location | Your repo | Google servers |
| Version control | Yes | No |
| Free tier | Unlimited | API rate limits |
| Privacy | Full control | Shared with Google |
| Backup | Automatic (Git) | Manual export |

---

## Next Steps

After data collection, analyze with:

```python
# Load data from data branch
import pandas as pd

df_demographics = pd.read_csv("study_data/demographics.csv")
df_sus = pd.read_csv("study_data/sus_responses.csv")
df_trust = pd.read_csv("study_data/trust_responses.csv")

# Run paired t-tests, ANOVAs, etc.
```

---

## Need Help?

Check [GitHub API documentation](https://docs.github.com/en/rest/repos/contents)

Or test locally first:
```bash
python -c "from utils.github_logger import GitHubLogger; logger = GitHubLogger()"
```
