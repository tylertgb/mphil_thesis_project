# TROUBLESHOOTING DATA LOGGING

**Issue:** Data not appearing after testing Group 2 apps

---

## WHERE DATA IS STORED

### **When Running LOCALLY (streamlit run):**
- Data saves to: `study_data/` folder in your project root
- Files: `demographics.csv`, `sus_responses.csv`, etc.
- This folder is created automatically when you log data

### **When Running on STREAMLIT CLOUD:**
- Data saves to: GitHub `data` branch in `study_data/` folder
- Requires: GitHub secrets configured (GITHUB_TOKEN, GITHUB_REPO)
- Falls back to ephemeral storage if secrets not configured

---

## QUICK CHECKS

### **1. Are you testing locally or on Streamlit Cloud?**

**If LOCAL:**
```bash
# Check if study_data folder was created
ls -la study_data/

# If it exists, check for new files
ls -lt study_data/
```

**If STREAMLIT CLOUD:**
- Data should appear in GitHub `data` branch
- Check: https://github.com/[your-repo]/tree/data/study_data

---

### **2. Did you complete the FULL flow?**

Data is only saved when you:
1. ✅ Complete demographics form
2. ✅ Complete at least one task case decision confidence
3. ✅ Click "Submit" on SUS/Trust/Understanding forms

**Partial completion = no data logged yet!**

---

### **3. Check for errors in the app**

When testing, look for:
- Red error messages
- "Connection error" warnings
- "Failed to log" messages

---

## FOR GROUP 2 APPS SPECIFICALLY

### **Expected Behavior:**

**Progressive FIRST app:**
1. Generates ID with `_G2` suffix (e.g., `P_20261115_143052_G2`)
2. Collects demographics → logs to `demographics.csv`
3. Task cases → logs to `decision_confidence.csv`
4. SUS/Trust/Understanding → logs to respective CSVs
5. All logs should have `order_group` field

**Static SECOND app:**
1. Requires ID with `_G2` suffix
2. Continues logging with same participant ID
3. Logs variant_a responses

---

## TESTING CHECKLIST

When testing Group 2 apps:

- [ ] **Start Progressive FIRST app**
- [ ] Complete demographics (should log immediately)
- [ ] Note your generated ID (ends with `_G2`?)
- [ ] Complete ONE task case confidence questionnaire
- [ ] **Check if data appears:**
  - Local: `study_data/demographics.csv` and `decision_confidence.csv`
  - Cloud: GitHub data branch
- [ ] If data appears → app is working!
- [ ] Complete SUS/Trust/Understanding
- [ ] Copy your Participant ID
- [ ] **Open Static SECOND app**
- [ ] Enter your ID (should be accepted)
- [ ] Complete one task
- [ ] **Check data again** (new variant_a entries)

---

## COMMON ISSUES

### **Issue: study_data folder doesn't exist locally**
**Cause:** Data hasn't been logged yet  
**Fix:** Complete at least demographics form

### **Issue: Data in data branch is old**
**Cause:** You're testing locally, not on deployed app  
**Fix:** That's expected! Local testing creates local files, not GitHub commits

### **Issue: No order_group field in logs**
**Cause:** Using old app files, not GROUP2 versions  
**Fix:** Make sure you're running:
- `app_with_study_GROUP2_FIRST.py` (not `app_with_study.py`)
- `app_with_study_GROUP2_SECOND.py` (not `app_with_study.py`)

### **Issue: Static SECOND rejects my _G2 ID**
**Cause:** ID format is wrong or missing _G2  
**Fix:** Copy exact ID from Progressive FIRST completion screen

---

## VERIFY DATA LOGGING IS WORKING

### **Quick Test:**

1. **Run Progressive FIRST locally:**
```bash
streamlit run interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py
```

2. **Complete demographics only**
3. **Check immediately:**
```bash
cat study_data/demographics.csv | tail -1
```

4. **Should see:**
- Your new participant ID ending with `_G2`
- Today's timestamp
- `order_group` field with `group2_progressive_first`

If you see this → logging works! ✅

---

## AFTER DEPLOYMENT

Once deployed to Streamlit Cloud:

1. Test the deployed URLs (not local)
2. Data should go to GitHub `data` branch
3. Check within 1-2 minutes after completing demographics
4. Git pull the data branch to see new files locally

---

## NEED MORE HELP?

Share:
1. Are you testing locally or on Streamlit Cloud?
2. Screenshot of any error messages
3. Last line of `demographics.csv` from data branch
4. Did you complete the full demographics form?
