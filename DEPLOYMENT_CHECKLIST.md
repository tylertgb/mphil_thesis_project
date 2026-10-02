# Deployment Checklist - GitHub API Solution

## ✅ What's Done

1. **GitHub API Logger** (`utils/github_logger.py`)
   - Writes all study data to GitHub `data` branch
   - No app restarts (separate from main branch)

2. **Session Persistence** (`participant_session.py`)
   - Tracks which variants completed per participant
   - Syncs across separate Streamlit Cloud apps
   - Validates Variant B access (must complete A first)

3. **Data Branch** Created
   - Branch: `data`
   - Contains: Study response CSVs
   - Isolated from code (no restarts)

4. **Documentation**
   - `GITHUB_API_SETUP.md` - Full setup guide
   - `GITHUB_LOGGER_QUICKSTART.md` - 15 min setup

---

## 🚀 Setup Steps (Do This Now)

### Step 1: Create GitHub Personal Access Token (5 min)

1. GitHub → Settings → Developer Settings
2. Personal Access Tokens → Tokens (classic)
3. Generate new token
4. **Scope:** Check `repo` (full repository access)
5. Copy token (starts with `ghp_...`)

---

### Step 2: Add Secrets to Streamlit Cloud (5 min × 3 apps)

Go to: https://share.streamlit.io/

**For each app** (Variant A, Variant B, Final Feedback):

1. Select app → **Settings** → **Secrets**
2. Add:

```toml
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
GITHUB_REPO = "tylertgb/mphil_thesis_project"
```

3. Click **Save**
4. Wait for app to restart (~1 min)

---

### Step 3: Test the System (10 min)

1. **Open Variant A deployed app**
   - Complete demographics
   - Complete a task
   - Complete questionnaires
   - Should see: "✅ Session saved for P006"

2. **Check GitHub data branch**
   ```bash
   git fetch origin data
   git checkout data
   cat study_data/active_sessions.csv
   ```
   Should see: `P006,True,False,2026-10-02T...`

3. **Open Variant B deployed app**
   - Should see: "🔗 Session synced via GitHub"
   - Should auto-load P006
   - Should allow access (Variant A completed)

4. **Test without Variant A**
   - Open Variant B in incognito/new browser
   - Should show: "❌ No active session found"
   - Should show retry button

---

## 🔍 What Happens Now

### Data Collection:
```
Participant response
  ↓
Dual Logger writes:
  1. Local CSV (backup) ✅
  2. GitHub data branch (cloud sync) ✅
  ↓
View anytime: git checkout data
```

### Session Tracking:
```
Variant A completed
  ↓
Saves: "P001, variant_a=True" to data branch
  ↓
Variant B opens
  ↓
Checks GitHub: "Did P001 complete variant_a?"
  ↓
Yes → Access granted ✅
No → Show error
```

---

## 📥 Retrieving Data

### Option A: Git Commands
```bash
# Fetch latest data
git fetch origin data
git checkout data

# View files
ls study_data/
cat study_data/demographics.csv

# Merge to main
git checkout main
git checkout data -- study_data/
git add study_data/
git commit -m "Update study data from cloud"
```

### Option B: GitHub Web UI
1. Go to your repo
2. Switch to **data** branch (dropdown)
3. Browse `study_data/` folder
4. Download individual CSV files

---

## 🎯 Participant Flow

### Step 1: Send Variant A Link
```
Subject: Research Study Participation - Part 1

Please access the first interface:
https://mphil-study-variant-a.streamlit.app

Complete all tasks and questionnaires.
Time: ~15 minutes
```

### Step 2: Send Variant B Link
```
Subject: Research Study Participation - Part 2

After completing Part 1, access the second interface:
https://mphil-study-variant-b.streamlit.app

Your session will continue automatically.
Time: ~15 minutes
```

### Step 3: Send Final Feedback Link
```
Subject: Research Study Participation - Final Feedback

Please complete the comparison questionnaire:
https://mphil-study-final-feedback.streamlit.app

Time: ~5 minutes
Thank you for participating!
```

---

## ⚠️ Troubleshooting

### "Authentication failed"
→ Check `GITHUB_TOKEN` in Streamlit secrets
→ Token might be expired (regenerate)

### "No active session found" (even after completing A)
→ Check Streamlit Cloud logs (Settings → Logs)
→ Look for GitHub API errors
→ Verify `GITHUB_REPO` format: `username/repo_name`

### Data not syncing
→ Check secrets configured in ALL 3 apps
→ Verify data branch exists: `git branch -r | grep data`
→ Check GitHub token has `repo` scope

### Session shows but can't access Variant B
→ Wait 30 seconds (GitHub API sync delay)
→ Click "🔄 Retry Loading Session" button
→ Check active_sessions.csv on data branch

---

## 📊 Monitoring Data Collection

### Real-time Monitoring:
```bash
# Watch for new data
watch -n 60 "git fetch origin data && git checkout data && wc -l study_data/*.csv"
```

### Check Participant Progress:
```bash
git checkout data
cat study_data/active_sessions.csv
```

Example output:
```
participant_id,variant_a_completed,variant_b_completed,timestamp
P001,True,True,2026-10-02T14:23:00
P002,True,False,2026-10-02T15:10:00  ← Still in progress
P003,True,True,2026-10-02T16:45:00
```

---

## ✅ Success Criteria

Your system is working when:

1. **Variant A completion** → Shows "✅ Session saved"
2. **Data branch updated** → CSV files contain new participant
3. **Variant B access** → Auto-loads participant, allows entry
4. **All data synced** → Demographics, SUS, trust, etc. in GitHub

---

## 🎓 For Your Thesis

**Advantages of This Solution:**
- ✅ No external dependencies (Google Sheets, Firebase)
- ✅ Data stays in your GitHub repo (version controlled)
- ✅ Free forever (GitHub API included)
- ✅ Transparent (see all data changes in Git history)
- ✅ Backup built-in (Git history + local CSV)

**Mention in Methodology:**
> "Participant data was collected using GitHub's REST API to write responses
> to a separate data branch, ensuring cross-app session persistence without
> requiring external database services. This approach maintained data
> sovereignty while enabling real-time cloud synchronization."

---

## 📝 Next Steps

1. ✅ Create GitHub token
2. ✅ Add secrets to all 3 Streamlit apps
3. ✅ Test complete flow (A → B → Final)
4. ✅ Recruit participants
5. ✅ Monitor data collection (`git checkout data`)
6. ✅ Run analysis after collection complete

---

**Need help?** Check logs in Streamlit Cloud (Settings → Logs) or test locally first!
