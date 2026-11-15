# COUNTERBALANCING IMPLEMENTATION PLAN

**Date:** November 15, 2026  
**Defense:** January 6-7, 2027  
**Timeline:** 7 weeks available

---

## 🎯 OBJECTIVE

Transform fixed-order design (all Static→Progressive) into counterbalanced design:
- **Group 1 (n=16):** Keep participants 1-16 → Static→Progressive  
- **Group 2 (n=15):** Re-collect participants 17-31 → **Progressive→Static**

---

## 📊 CURRENT DEPLOYMENT (Fixed Order)

**Existing URLs (per your previous messages):**
1. https://mphil-study-variant-a.streamlit.app (Static - FIRST)
2. https://mphil-study-variant-b.streamlit.app (Progressive - SECOND)
3. https://mphil-study-final-feedback.streamlit.app (Final feedback)

**Current flow:** All participants do 1 → 2 → 3

---

## 🔧 NEW DEPLOYMENT STRATEGY

### **Option A: URL-Based Routing (RECOMMENDED)**

Create **TWO entry points** with different orders:

**Group 1 (Static→Progressive) - KEEP EXISTING:**
- URL 1a: https://mphil-study-variant-a.streamlit.app
- URL 1b: https://mphil-study-variant-b.streamlit.app  
- URL 1c: https://mphil-study-final-feedback.streamlit.app
- **Participants:** First 16 (already collected, no changes)

**Group 2 (Progressive→Static) - NEW DEPLOYMENT:**
- URL 2a: https://mphil-study-variant-b-first.streamlit.app (Progressive FIRST)
- URL 2b: https://mphil-study-variant-a-second.streamlit.app (Static SECOND)
- URL 2c: https://mphil-study-final-feedback.streamlit.app (Same final feedback)
- **Participants:** Last 15 (re-collect with reversed order)

### **Option B: Single Entry Point with Order Parameter**

Create a unified study app that assigns order based on participant ID:
- URL: https://mphil-study.streamlit.app?order=group1 or order=group2
- App internally routes to correct interface sequence
- **Advantage:** Cleaner, single deployment
- **Disadvantage:** More complex implementation

**RECOMMENDATION: Use Option A for simplicity and speed**

---

## 📝 IMPLEMENTATION STEPS

### **Step 1: Identify Re-Collection Participants (1 hour)**

**Action needed from you:**
- Provide list of last 15 participants (IDs 17-31 by collection date)
- OR: Give me the participant IDs you want to re-collect

**I'll create:**
- Re-invitation contact list
- Tracking spreadsheet (who agreed, who completed)

### **Step 2: Create Reversed-Order Apps (2-3 hours)**

**I'll create:**

1. **`interfaces/variant_b_progressive/app_with_study_FIRST.py`**
   - Modified to be the FIRST interface
   - Collects demographics
   - Uses condition = 'variant_b' (keeping consistent naming)
   - Instructs: "After completing, go to Variant A (Static) link"

2. **`interfaces/variant_a_static/app_with_study_SECOND.py`**  
   - Modified to be the SECOND interface
   - Requires participant ID from first interface
   - Uses condition = 'variant_a'
   - Instructs: "After completing, go to Final Feedback link"

3. **Update `final_feedback_app.py`**
   - Already works for both orders (it's condition-agnostic)
   - No changes needed

### **Step 3: Data Logging Strategy (1 hour)**

**Participant ID format:**

**Group 1 (existing):** Keep as-is
- Example: `P_20261003_085342`

**Group 2 (re-collection):**  
**Option A - New IDs with suffix:**
- Example: `P_20261003_085342_G2` or `P_20261003_085342_REV`
- **Advantage:** Clear differentiation
- **Disadvantage:** Slightly messier

**Option B - Completely new IDs:**
- Example: `P_20261120_143052` (new timestamp)
- **Advantage:** Clean, treats as "new" participants
- **Disadvantage:** Lose link to original if needed

**RECOMMENDATION: Option A (suffix) for traceability**

### **Step 4: Update Data Logger (1 hour)**

**Add order group field to all logs:**
```python
{
    'participant_id': 'P_XXX',
    'order_group': 'group1_static_first' or 'group2_progressive_first',
    'condition': 'variant_a' or 'variant_b',
    ...
}
```

This enables proper analysis of order effects.

### **Step 5: Testing (2-3 hours)**

**Test both flows completely:**
1. Group 1 flow: Static→Progressive→Final (existing, verify still works)
2. Group 2 flow: Progressive→Static→Final (new, test thoroughly)

**Checklist:**
- [ ] Participant ID carries through correctly
- [ ] All questionnaires log properly
- [ ] Data goes to correct GitHub branch/folder
- [ ] Final feedback app accepts both order groups
- [ ] No crashes or data loss

### **Step 6: Deploy (1-2 hours)**

**Streamlit deployment:**
- Deploy new apps to Streamlit Cloud
- Get new URLs for Group 2
- Test live deployment
- Create deployment documentation

### **Step 7: Prepare Participant Communication (1 hour)**

**I'll create:**
- Re-invitation email template
- Study instructions for Group 2
- Consent update (if needed)
- FAQ for participants

---

## 📧 PARTICIPANT RE-INVITATION STRATEGY

### **Email Template (Draft)**

```
Subject: Research Study Follow-Up - Your Participation Requested Again

Dear [Participant Name],

Thank you for participating in our AI interface study [date of original participation]. 

To strengthen the scientific rigor of our findings, we are implementing a 
counterbalanced study design and would greatly appreciate your participation 
once more.

What's different this time:
• You will experience the interfaces in REVERSE order (Progressive first, 
  then Static)
• Same tasks and questionnaires (~25-30 minutes total)
• Your new responses will replace your previous data in our analysis
• This helps us rule out practice effects and strengthen causal claims

Why this matters:
Your repeated participation allows us to determine whether differences between 
interfaces are due to interface design or order of presentation. This is 
methodologically important for publication and validation of findings.

Timeline:
• Participation needed: By [date - suggest Nov 30]
• Study links: [Group 2 URLs provided below]

[Optional: Compensation/token of appreciation]

Your continued support is invaluable. If you have any questions, please don't 
hesitate to reach out.

Best regards,
[Your name]

STUDY LINKS (Please complete in this order):
1. Progressive Interface (FIRST): [URL]
2. Static Interface (SECOND): [URL]  
3. Final Feedback: [URL]
```

### **Follow-up Strategy**

**Day 1:** Send invitation
**Day 3:** Reminder to non-responders
**Day 5:** Final reminder
**Day 7:** Close collection, proceed with those who completed

**Target:** 12-15 completions out of 15 invited (80-100%)

---

## 📊 NEW ANALYSIS APPROACH

### **Analysis Script Updates**

**Current:** Paired t-test / Wilcoxon (within-subjects only)

**New:** Mixed ANOVA / Mixed-effects model
```
DV: Trust, Confidence, SUS
IV1: Condition (Static vs Progressive) - within
IV2: Order (Static-first vs Progressive-first) - between
Interaction: Condition × Order
```

**Key questions:**
1. **Main effect of Condition?** (controlling for order) → True treatment effect
2. **Main effect of Order?** → Practice/fatigue effects
3. **Interaction?** → Does order moderate treatment effect?

**Best outcome:** Significant condition effect, no interaction
**Good outcome:** Significant condition effect, small interaction  
**Challenging outcome:** Large interaction (order explains most variance)

### **Updated Scripts I'll Create**

1. `run_hypothesis_tests_COUNTERBALANCED.py` - Mixed ANOVA analysis
2. `visualize_order_effects.py` - Interaction plots
3. `compare_order_groups.py` - Descriptive comparison

---

## ⏱️ TIMELINE

### **Week 1 (Nov 15-22): Implementation**
- [ ] Day 1-2: Create reversed-order apps
- [ ] Day 3: Test both flows thoroughly
- [ ] Day 4: Deploy to Streamlit Cloud
- [ ] Day 5: Prepare participant communication
- [ ] Day 6-7: Buffer/fixes

### **Week 2 (Nov 23-30): Re-Collection**
- [ ] Day 8: Send re-invitations  
- [ ] Day 10: First reminder
- [ ] Day 12: Second reminder
- [ ] Day 14: Close collection

### **Week 3 (Dec 1-7): Analysis**
- [ ] Day 15-16: Clean and merge data
- [ ] Day 17-18: Run counterbalanced analysis
- [ ] Day 19-20: Create new tables/figures
- [ ] Day 21: Document results

### **Week 4-7 (Dec 8 - Jan 5): Thesis Revision**
- [ ] Update Chapter 3 (counterbalanced design)
- [ ] Rewrite Chapter 4 (order analysis)
- [ ] Strengthen Chapter 5 (causal claims!)
- [ ] Buffer for revisions

**BUFFER: 3+ weeks before defense on Jan 6-7**

---

## 🎯 SUCCESS CRITERIA

### **Minimum Success:**
- 12+ participants complete Group 2 (Progressive→Static)
- Final n = 28+ (16 Group 1 + 12 Group 2)
- Can run order analysis

### **Target Success:**
- 15 participants complete Group 2
- Final n = 31 (16 Group 1 + 15 Group 2)  
- Balanced design, full power

### **Excellent Success:**
- 15 complete Group 2
- H3/H4 remain significant with order controlled
- Can make causal claims
- Publishable in CHI/top venues

---

## ❓ DECISIONS NEEDED FROM YOU

Please confirm:

1. **Participant Selection:**
   - [ ] Which 15 participants to re-collect? (provide IDs)
   - [ ] OR: Use last 15 by collection date?

2. **Participant ID Strategy:**
   - [ ] Option A: Add suffix (e.g., P_XXX_G2)
   - [ ] Option B: Generate new IDs

3. **Deployment:**
   - [ ] Confirm you can deploy new Streamlit apps (or I guide you)
   - [ ] Confirm GitHub data logging still works

4. **Ethics/Compensation:**
   - [ ] Any ethics approval update needed for re-collection?
   - [ ] Offering compensation/incentive?

---

## 🚀 READY TO START?

**Once you confirm the above, I'll immediately begin:**
1. Creating reversed-order app files
2. Writing deployment instructions
3. Preparing participant communication templates
4. Updating analysis scripts

**Estimated implementation time: 6-8 hours of work (over 2-3 days)**

Let me know your decisions and we'll get started! 💪
