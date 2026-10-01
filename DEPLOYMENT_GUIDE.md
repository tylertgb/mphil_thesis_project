# 🚀 Streamlit Cloud Deployment Guide

## Overview

This guide explains how to deploy your study interfaces online using **Streamlit Community Cloud** (FREE) with GitHub-based CSV storage.

---

## ✅ Prerequisites

1. ✅ GitHub repository with code (done)
2. ✅ Streamlit Cloud account (create at https://streamlit.io/cloud)
3. ✅ Your 3 existing participant responses are already in `study_data/` (preserved)

---

## 📋 Step-by-Step Deployment

### **Step 1: Deploy Variant A to Streamlit Cloud**

1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Fill in the form:
   - **Repository:** `tylertgb/mphil_thesis_project`
   - **Branch:** `main`
   - **Main file path:** `interfaces/variant_a_static/app_with_study.py`
   - **App URL:** Choose a custom name like `mphil-study-variant-a`
4. Click **"Deploy"**
5. Wait 2-3 minutes for deployment
6. **Copy the URL** (e.g., `https://mphil-study-variant-a.streamlit.app`)

### **Step 2: Deploy Variant B**

1. Click **"New app"** again
2. Fill in:
   - **Repository:** `tylertgb/mphil_thesis_project`
   - **Branch:** `main`
   - **Main file path:** `interfaces/variant_b_progressive/app_with_study.py`
   - **App URL:** `mphil-study-variant-b`
3. Click **"Deploy"**
4. **Copy the URL**

### **Step 3: Deploy Final Feedback**

1. Click **"New app"** again
2. Fill in:
   - **Repository:** `tylertgb/mphil_thesis_project`
   - **Branch:** `main`
   - **Main file path:** `interfaces/final_feedback_app.py`
   - **App URL:** `mphil-study-final-feedback`
3. Click **"Deploy"**
4. **Copy the URL**

---

## 📊 How Data Collection Works

### **CSV Storage on GitHub:**

1. Participants complete tasks → responses logged to CSV files
2. CSV files are stored in the Streamlit Cloud container
3. **You need to periodically download the data from GitHub**

### **Downloading Data:**

Every few participants (or daily), pull the updated CSVs:

```powershell
git pull origin main
```

The CSV files in `study_data/` will be updated with new participant responses.

---

## 👥 Participant Flow

### **Share These 3 URLs with Participants:**

1. **Variant A:** `https://mphil-study-variant-a.streamlit.app`
2. **Variant B:** `https://mphil-study-variant-b.streamlit.app`
3. **Final Feedback:** `https://mphil-study-final-feedback.streamlit.app`

### **Instructions for Participants:**

```
Dear Participant,

Thank you for participating in my MPhil research study!

Please follow these steps:

1. Complete Variant A: [Variant A URL]
   - Takes ~10-15 minutes
   - Note your Participant ID shown at the end

2. Complete Variant B: [Variant B URL]
   - Your session will continue automatically
   - Takes ~10-15 minutes

3. Complete Final Feedback: [Final Feedback URL]
   - Takes ~3-5 minutes

Please complete all three in one sitting if possible.

Best regards,
[Your Name]
```

---

## ⚠️ Important Considerations

### **Data Persistence:**

- ✅ CSV files persist in Streamlit Cloud
- ✅ Automatic commits to GitHub every time data is logged
- ⚠️ App restarts (after updates) won't lose data
- ⚠️ Session state is per-user (isolated)

### **Concurrent Users:**

- ✅ Thread-safe file locking implemented
- ✅ Multiple participants can use simultaneously
- ✅ Each gets unique Participant ID (P001, P002, P003...)

### **Ethics & Privacy:**

- ⚠️ Update your ethics approval if needed (online vs in-person)
- ⚠️ Add informed consent screen if required
- ⚠️ Data is stored on GitHub (check if this is compliant)

---

## 🔧 Troubleshooting

### **App is Sleeping:**

- Streamlit Cloud puts inactive apps to sleep
- They wake up in ~30 seconds when accessed
- This is normal and won't affect data

### **Participant ID Not Carrying Over:**

- Check that `.active_session.json` is being created
- Verify `study_data/` folder has write permissions
- Session file persists across Variant A → B

### **CSV Files Not Updating:**

- Check Streamlit Cloud logs (click "Manage app" → "Logs")
- Verify file locking is working
- Try pulling from GitHub: `git pull origin main`

---

## 📈 Monitoring

### **Check Logs:**

1. Go to https://share.streamlit.io/
2. Click on your app
3. Click **"Manage app"** → **"Logs"**
4. Look for errors or participant activity

### **Download Data:**

Periodically run:
```powershell
git pull origin main
```

Check `study_data/` for new CSV entries.

---

## 🎯 URLs to Share

Once deployed, update this section with your actual URLs:

- **Variant A:** ______________________________
- **Variant B:** ______________________________
- **Final Feedback:** _______________________________

---

## 📝 Next Steps After Deployment

1. ✅ Test all three apps yourself
2. ✅ Verify session persistence (A → B → Final)
3. ✅ Check CSV files are being created/updated
4. ✅ Share URLs with pilot participants
5. ✅ Monitor logs for first few participants
6. ✅ Pull data regularly: `git pull origin main`

---

## 🆘 Need Help?

If something goes wrong:
1. Check Streamlit Cloud logs
2. Verify GitHub repo is accessible
3. Test locally first: `streamlit run interfaces/variant_a_static/app_with_study.py`
4. Check if CSV files are being written locally

Good luck with your data collection! 🎓
