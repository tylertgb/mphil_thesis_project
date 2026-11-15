# GROUP 2 APPS IMPLEMENTATION - Progressive→Static Order

**For Re-Collection of Participants 17-31**

---

## 🎯 STRATEGY

Since you already have 3 deployed Streamlit apps, we'll create **2 modified versions** for Group 2:

### **Current Apps (Group 1 - Keep as-is):**
1. Variant A Static (FIRST) - collects demographics
2. Variant B Progressive (SECOND) - requires participant ID
3. Final Feedback - works for both

### **New Apps (Group 2 - To Create):**
1. **Variant B Progressive (FIRST)** - NEW: collects demographics, adds `_G2` suffix
2. **Variant A Static (SECOND)** - NEW: requires participant ID from Progressive
3. Final Feedback - SAME (already works for both)

---

## 📝 KEY MODIFICATIONS NEEDED

### **Modification 1: Add Order Group to Data Logging**

All logs need to include `order_group` field:
- `"group1_static_first"` for existing Group 1
- `"group2_progressive_first"` for new Group 2

### **Modification 2: Participant ID Suffix**

Group 2 participant IDs get `_G2` suffix:
- Example: `P_20261003_085342_G2`

### **Modification 3: Demographics Collection**

Progressive app (Group 2) must collect demographics FIRST (like Static does for Group 1)

---

## 🔧 FILES TO CREATE

I'll create 2 new files in your repo:

### **File 1: `interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py`**

**Purpose:** Progressive interface as FIRST interface for Group 2
- Collects demographics
- Generates participant ID with `_G2` suffix  
- Logs with `order_group = "group2_progressive_first"`
- Shows instruction: "Next, go to Variant A (Static)"

### **File 2: `interfaces/variant_a_static/app_with_study_GROUP2_SECOND.py`**

**Purpose:** Static interface as SECOND interface for Group 2
- Requires participant ID from Progressive
- Validates ID has `_G2` suffix
- Logs with `order_group = "group2_progressive_first"`
- Shows instruction: "Next, go to Final Feedback"

---

## 🚀 DEPLOYMENT STEPS

### **Step 1: I Create the Files (Today)**
- Generate both modified app files
- Test locally
- Commit to GitHub

### **Step 2: You Deploy to Streamlit Cloud (Tomorrow)**

**Deploy App 1: Progressive FIRST**
1. Go to Streamlit Cloud dashboard
2. Create new app
3. Point to: `interfaces/variant_b_progressive/app_with_study_GROUP2_FIRST.py`
4. Suggested URL: `mphil-study-progressive-first` or `mphil-study-group2-part1`
5. Deploy

**Deploy App 2: Static SECOND**
1. Create new app
2. Point to: `interfaces/variant_a_static/app_with_study_GROUP2_SECOND.py`
3. Suggested URL: `mphil-study-static-second` or `mphil-study-group2-part2`
4. Deploy

**Existing App: Final Feedback**
- No changes needed
- URL stays: `mphil-study-final-feedback`

### **Step 3: Test Complete Flow (Tomorrow)**
1. Go through full Group 2 flow yourself
2. Verify participant ID carries through
3. Check data logs in GitHub data branch
4. Confirm `_G2` suffix and `order_group` field

---

## 📧 PARTICIPANT INSTRUCTIONS (Group 2)

**Email Template:**

```
Subject: Research Study Follow-Up - Your Participation Needed Again

Dear [Participant],

Thank you for participating in our AI interface study earlier. To strengthen 
our research findings, we are implementing a counterbalanced design and would 
appreciate your participation once more.

What's different:
• You will experience the interfaces in REVERSE order (Progressive first, 
  then Static)
• Same tasks and questionnaires (~25-30 minutes total)
• Your new responses will be used in the final analysis

IMPORTANT: Please complete in this exact order:

1. FIRST: Progressive Interface
   https://[your-progressive-first-url].streamlit.app
   
2. THEN: Static Interface  
   https://[your-static-second-url].streamlit.app
   
3. FINALLY: Final Feedback
   https://mphil-study-final-feedback.streamlit.app

Timeline: Please complete by [date - suggest Nov 30]

Your continued support is invaluable to this research. Thank you!

Best regards,
[Your name]
```

---

## 📊 DATA LOGGING STRUCTURE

### **Group 1 (Existing - No Changes):**

```python
{
    'participant_id': 'P_20261003_085342',
    'order_group': 'group1_static_first',
    'condition': 'variant_a' or 'variant_b',
    ...
}
```

### **Group 2 (New):**

```python
{
    'participant_id': 'P_20261003_085342_G2',  # Note _G2 suffix
    'order_group': 'group2_progressive_first',
    'condition': 'variant_a' or 'variant_b',
    ...
}
```

---

## 🔍 ANALYSIS UPDATES

### **Clean Data Script Update:**

```python
# Parse order group from participant ID suffix
df['order_group'] = df['participant_id'].apply(
    lambda x: 'group2_progressive_first' if x.endswith('_G2') 
    else 'group1_static_first'
)

# Create numeric order variable
df['order_numeric'] = df['order_group'].map({
    'group1_static_first': 1,
    'group2_progressive_first': 2
})
```

### **New Analysis Script: `run_hypothesis_tests_COUNTERBALANCED.py`**

```python
# Mixed ANOVA
# DV: trust_score, confidence_score, sus_score
# IV1: Condition (Static vs Progressive) - within-subjects
# IV2: Order Group (Static-first vs Progressive-first) - between-subjects
# Interaction: Condition × Order

from statsmodels.stats.anova import AnovaRM

# Example for Trust
aov = AnovaRM(
    data=df_long,
    depvar='trust',
    subject='participant_id',
    within=['condition'],
    between=['order_group']
).fit()
```

---

## ✅ VERIFICATION CHECKLIST

Before contacting participants, verify:

- [ ] Both Group 2 apps deployed successfully
- [ ] Test flow: Progressive→Static→Final Feedback
- [ ] Participant ID gets `_G2` suffix
- [ ] Data logs to GitHub data branch
- [ ] `order_group` field present in all logs
- [ ] Final feedback app accepts Group 2 IDs

---

## 🎯 PARTICIPANTS TO RE-COLLECT

**From your answer: Participants 17-31**

You'll need to:
1. Get their contact information
2. Send re-invitation email
3. Track responses (who agrees, who completes)
4. Follow up with reminders

**Target: 12-15 completions (80-100%)**

---

## 📅 TIMELINE

**Today (Nov 15):**
- I create the 2 modified app files
- You review and approve

**Tomorrow (Nov 16-17):**
- You deploy to Streamlit Cloud
- Test complete flow

**Next Week (Nov 18-24):**
- Send re-invitations to participants 17-31
- First reminder on Day 3
- Second reminder on Day 5

**End of Month (Nov 25-30):**
- Close re-collection
- Should have 12-15 completions

**Early December (Dec 1-7):**
- Run counterbalanced analysis
- Update tables and figures

---

## 🚀 READY TO PROCEED?

Confirm you're ready, and I'll immediately generate:
1. `app_with_study_GROUP2_FIRST.py` (Progressive first)
2. `app_with_study_GROUP2_SECOND.py` (Static second)
3. Updated `dual_logger.py` to handle order groups
4. Participant re-invitation email template
5. Deployment instructions

**Say "Generate the files" and I'll start!** 💪
