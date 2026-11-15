# UPDATE URLs AFTER DEPLOYMENT

**After you deploy both Group 2 apps to Streamlit Cloud, you MUST update the link URLs.**

---

## 📝 WHAT TO UPDATE

### **File 1: Progressive FIRST App**

**Location:** `interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py`

**Lines to update:** ~545 and ~555

**Find:**
```python
st.link_button(
    "Open Part 2: Static Interface",
    "https://YOUR_STATIC_SECOND_URL_HERE.streamlit.app",
    use_container_width=True,
    type="primary"
)
```

**Replace with your actual Static SECOND URL:**
```python
st.link_button(
    "Open Part 2: Static Interface",
    "https://mphil-study-static-second.streamlit.app",  # ← YOUR ACTUAL URL
    use_container_width=True,
    type="primary"
)
```

**Also update the backup link text (line ~555):**
```
**Alternative: Copy this link if button doesn't work**
```
https://mphil-study-static-second.streamlit.app  # ← YOUR ACTUAL URL
```
```

---

## 🚀 DEPLOYMENT WORKFLOW

### **Step 1: Deploy Both Apps**

1. Deploy **Progressive FIRST** to Streamlit Cloud
   - Get URL (e.g., `https://mphil-study-progressive-first.streamlit.app`)
   
2. Deploy **Static SECOND** to Streamlit Cloud
   - Get URL (e.g., `https://mphil-study-static-second.streamlit.app`)

### **Step 2: Add GitHub Secrets to Both Apps**

For EACH app, add in Settings → Secrets:
```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO = "tylertgb/mphil_thesis_project"
```

### **Step 3: Update the Link URL**

1. Open: `interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py`
2. Replace `YOUR_STATIC_SECOND_URL_HERE` with your actual Static SECOND URL
3. Commit and push to GitHub:
   ```bash
   git add interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py
   git commit -m "Update Static SECOND link URL"
   git push origin main
   ```
4. Wait 1-2 minutes - Streamlit Cloud auto-redeploys!

### **Step 4: Test Complete Flow**

1. Open Progressive FIRST app
2. Complete demographics (note your P_XXX_G2 ID)
3. Complete one task
4. Click "Open Part 2" button
5. Should open Static SECOND app
6. Enter your P_XXX_G2 ID
7. Should be accepted ✅

---

## ✅ VERIFICATION CHECKLIST

After updating URLs:

- [ ] Progressive FIRST button works and opens Static SECOND
- [ ] Static SECOND accepts _G2 participant IDs
- [ ] Static SECOND button works and opens Final Feedback
- [ ] Data logs to GitHub `data` branch with `order_group` field
- [ ] Complete flow works end-to-end

---

## 📋 YOUR DEPLOYMENT URLs

Fill these in after deployment:

**GROUP 2 APPS:**
- Progressive FIRST: `https://___________________________.streamlit.app`
- Static SECOND: `https://___________________________.streamlit.app`

**SHARED:**
- Final Feedback: `https://mphil-study-final-feedback.streamlit.app` ✅ (already deployed)

---

## 🔄 IF YOU NEED TO CHANGE URLS LATER

If you rename your Streamlit apps:

1. Update the URL in the code (line ~545)
2. Commit and push
3. Streamlit auto-redeploys (1-2 min)
4. Test the link again

---

## 📧 EMAIL TEMPLATE UPDATE

After deployment, update `GROUP2_EMAIL_TEMPLATE.txt` with your actual URLs:

**Replace:**
```
1. Progressive (First): [YOUR_URL_1_HERE]
2. Static (Second): [YOUR_URL_2_HERE]
```

**With:**
```
1. Progressive (First): https://mphil-study-progressive-first.streamlit.app
2. Static (Second): https://mphil-study-static-second.streamlit.app
```

---

**Done! You're ready to invite participants!** 🎉
