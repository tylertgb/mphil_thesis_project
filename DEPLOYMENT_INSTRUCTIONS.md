# STREAMLIT DEPLOYMENT INSTRUCTIONS - GROUP 2 APPS

**Deploy 2 new Streamlit apps for counterbalanced Group 2 (Progressive→Static order)**

---

## 📋 PREREQUISITES

- [x] Streamlit Cloud account (you already have this)
- [x] GitHub repo connected to Streamlit
- [x] Existing 3 apps already deployed

---

## 🚀 DEPLOYMENT STEPS

### **APP 1: Progressive Interface (FIRST)**

1. **Go to Streamlit Cloud Dashboard**
   - Visit: https://share.streamlit.io/
   - Sign in with your account

2. **Click "New app"**

3. **Configure App Settings:**
   - **Repository:** [Your GitHub repo name]
   - **Branch:** `main`
   - **Main file path:** `interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py`
   - **App URL (custom):** `mphil-study-progressive-first` (or any name you prefer)

4. **Advanced Settings (Optional):**
   - Python version: 3.9+ (default is fine)
   - Leave secrets blank (unless you have GitHub API tokens)

5. **Click "Deploy"**

6. **Wait 2-3 minutes** for app to build and deploy

7. **Test the app:**
   - Click through to verify it works
   - Check that it generates Participant ID with `_G2` suffix
   - Verify demographics form appears

8. **SAVE THE URL** - you'll need this for participant emails

---

### **APP 2: Static Interface (SECOND)**

1. **Click "New app" again**

2. **Configure App Settings:**
   - **Repository:** [Same repo]
   - **Branch:** `main`
   - **Main file path:** `interfaces/variant_a_static/app_with_study_GROUP2_SECOND.py`
   - **App URL (custom):** `mphil-study-static-second` (or any name you prefer)

3. **Click "Deploy"**

4. **Wait 2-3 minutes**

5. **Test the app:**
   - Try entering a test ID ending with `_G2`
   - Verify it accepts the ID
   - Check that it rejects IDs without `_G2` suffix

6. **SAVE THE URL**

---

## ✅ POST-DEPLOYMENT TESTING

### **Full Flow Test:**

1. **Start at App 1 (Progressive FIRST):**
   - URL: https://[your-progressive-first-url].streamlit.app
   - Complete demographics
   - Note the Participant ID generated (should end with `_G2`)
   - Complete at least one task case
   - Note: You can skip the full study for testing

2. **Continue to App 2 (Static SECOND):**
   - URL: https://[your-static-second-url].streamlit.app
   - Enter the Participant ID from Step 1
   - Verify it accepts the ID
   - Check that task cases load

3. **Check Data Logging:**
   - Go to your GitHub repo
   - Check the `data` branch (if using GitHub logging)
   - OR check local `study_data/` folder
   - Verify `order_group` field is present and says `"group2_progressive_first"`

---

## 📝 YOUR APP URLS

Once deployed, fill in these URLs:

**GROUP 1 (Existing - No Changes):**
- Static (First): https://mphil-study-variant-a.streamlit.app
- Progressive (Second): https://mphil-study-variant-b.streamlit.app
- Final Feedback: https://mphil-study-final-feedback.streamlit.app

**GROUP 2 (New - Just Deployed):**
- Progressive (First): https://_____________________________.streamlit.app
- Static (Second): https://_____________________________.streamlit.app
- Final Feedback: https://mphil-study-final-feedback.streamlit.app (SAME)

---

## 🔍 TROUBLESHOOTING

### **Issue: App won't deploy**
- **Check:** File path is correct (case-sensitive!)
- **Check:** Branch is `main` (not `master` or `data`)
- **Fix:** Verify file exists at exact path

### **Issue: Import errors**
- **Check:** All required packages in `requirements.txt`
- **Fix:** Add missing packages to requirements.txt and redeploy

### **Issue: Participant ID not generated with _G2**
- **Check:** You deployed the correct file (`app_with_study_GROUP2_FIRST.py`)
- **Not:** The old file (`app_with_study.py`)

### **Issue: Static app rejects valid _G2 IDs**
- **Check:** You deployed `app_with_study_GROUP2_SECOND.py`
- **Check:** ID format is correct: `P_20261115_143052_G2`

### **Issue: Data not logging to GitHub**
- **Expected:** Data logs to CSV files in `study_data/` folder
- **GitHub logging:** Requires GitHub secrets configured (optional)
- **Fix:** Check logs locally, GitHub sync is optional

---

## 📧 NEXT STEPS

After successful deployment:

1. ✅ Test both apps completely
2. ✅ Verify data logging works
3. ✅ Update participant email template with your URLs
4. ✅ Send invitations to participants 17-31
5. ✅ Track responses in spreadsheet
6. ✅ Monitor data collection

---

## 🛠️ IF YOU NEED TO UPDATE APPS

After initial deployment, if you need to change the code:

1. Make changes to the `.py` files locally
2. Commit and push to GitHub `main` branch
3. Streamlit auto-detects changes and redeploys (takes 1-2 min)
4. No manual redeployment needed!

---

## 📊 MONITORING

**Check deployment status:**
- Streamlit dashboard shows app status (running/stopped/error)
- View logs in Streamlit Cloud for debugging

**Check data collection:**
- Monitor GitHub `data` branch for new files
- OR check local `study_data/` folder

**Expected files:**
- `demographics_log.csv`
- `sus_log.csv`
- `trust_log.csv`
- `understanding_log.csv`
- `decision_confidence_log.csv`

All should have `order_group` column with `group2_progressive_first` for new participants.

---

## ✨ DONE!

You're ready to start re-collecting data from Group 2! 🎉
