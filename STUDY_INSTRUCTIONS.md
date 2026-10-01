# User Study Guide - Digital Questionnaire System

## 📋 Overview

This study uses **integrated digital questionnaires** where participants fill forms directly in the system. All responses are automatically logged to CSV files.

**Quick Commands:**
```powershell
# Run these 3 commands for each participant:
streamlit run interfaces/variant_a_static/app_with_study.py
streamlit run interfaces/variant_b_progressive/app_with_study.py
streamlit run interfaces/final_feedback_app.py
```

---

## 🎯 Study Flow

### **Phase 1: Variant A (Static Interface)**

**File:** `interfaces/variant_a_static/app_with_study.py`

1. ✅ Welcome screen → Auto-generate Participant ID (e.g., P001, P002...)
2. ✅ Section A: Demographics (7 questions)
3. ✅ Task Case 1 (high_risk_1) → Prediction → Decision Confidence (4 items)
4. ✅ Task Case 2 (medium_risk_4) → Prediction → Decision Confidence (4 items)
5. ✅ Task Case 3 (low_risk_7) → Prediction → Decision Confidence (4 items)
6. ✅ Section B: SUS (10 items)
7. ✅ Section C: Trust (5 items)
8. ✅ Section D: Understanding (5 items)
9. ✅ Completion message

**Estimated time:** 10-12 minutes

---

### **Phase 2: Variant B (Progressive Interface)**

**File:** `interfaces/variant_b_progressive/app_with_study.py`

1. ✅ Resume with same Participant ID from Variant A
2. ✅ Task Case 1 (high_risk_2) → Prediction + SHAP → Decision Confidence (4 items)
3. ✅ Task Case 2 (medium_risk_5) → Prediction + SHAP → Decision Confidence (4 items)
4. ✅ Task Case 3 (low_risk_8) → Prediction + SHAP → Decision Confidence (4 items)
5. ✅ Section B: SUS (10 items)
6. ✅ Section C: Trust (5 items)
7. ✅ Section D: Understanding (5 items)
8. ✅ Completion message

**Estimated time:** 12-15 minutes (longer due to reading explanations)

---

### **Phase 3: Final Feedback**

**File:** `interfaces/final_feedback_app.py`

1. ✅ Section F: Qualitative Feedback (4 open-ended questions)
2. ✅ Thank you + completion

**Estimated time:** 3-5 minutes

---

## 🚀 How to Run the Study

### **Setup (Once, before first participant):**

1. Open terminal/PowerShell in project directory
2. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
3. Verify `study_data/` folder exists (created automatically)

---

### **For Each Participant:**

#### **Step 1: Run Variant A**

```powershell
streamlit run interfaces/variant_a_static/app_with_study.py
```

- Browser opens automatically
- Participant completes all steps
- **Participant ID auto-generated** (P001, P002, P003...)
- All responses auto-saved to `study_data/`

---

#### **Step 2: Run Variant B**

**Close Variant A window first**, then:

```powershell
streamlit run interfaces/variant_b_progressive/app_with_study.py
```

- Browser opens automatically
- **Same Participant ID** continues from Variant A session
- All responses auto-saved to `study_data/`

---

#### **Step 3: Run Final Feedback**

**Close Variant B window first**, then:

```powershell
streamlit run interfaces/final_feedback_app.py
```

- Browser opens automatically
- **Same Participant ID** continues
- Section F qualitative responses auto-saved
- Study complete! ✅

---

## 📊 Data Collection

### **Output Files (in `study_data/`):**

| File | Content | Rows per Participant |
|------|---------|---------------------|
| `demographics.csv` | Section A responses | 1 |
| `sus_responses.csv` | SUS scores (A & B) | 2 |
| `trust_responses.csv` | Trust scores (A & B) | 2 |
| `understanding_responses.csv` | Understanding scores (A & B) | 2 |
| `decision_confidence.csv` | Decision confidence (A & B, 3 tasks each) | 6 |
| `qualitative_feedback.csv` | Section F open-ended | 1 |
| `session_metadata.json` | Session tracking | 1 |

**Total:** 15 rows of data per participant

---

## ✅ Session Checklist

### **Before Each Session:**

- [ ] Check `study_data/` folder exists
- [ ] Terminal ready with venv activated
- [ ] Browser available (Chrome/Edge recommended)

### **During Session:**

- [ ] Run Variant A → Participant completes → Note Participant ID
- [ ] Run Variant B → Same Participant ID continues
- [ ] Run Final Feedback → Complete
- [ ] Verify CSV files updated (check file timestamps)

### **After Session:**

- [ ] Close all browser windows
- [ ] Check `study_data/` for new entries
- [ ] Ready for next participant

---

## 🔧 Troubleshooting

### **Problem: "No participant session found" in Variant B**

**Cause:** Streamlit cleared session state between apps  
**Solution:** Use the "Start New Session (Testing)" button for testing, or ensure same browser session

### **Problem: Participant ID not auto-generated**

**Cause:** `demographics.csv` file missing or corrupted  
**Solution:** Delete `study_data/` folder and restart

### **Problem: Form submission doesn't work**

**Cause:** Incomplete form (missing required fields)  
**Solution:** Check for validation errors (red text) and complete all fields

### **Problem: Browser doesn't open automatically**

**Cause:** Port already in use  
**Solution:** 
```powershell
streamlit run app.py --server.port 8502
```

---

## 📈 Data Analysis

### **After All Participants Complete:**

Run the export script:

```python
from study_response_logger import export_for_analysis
export_for_analysis(output_dir="study_data", analysis_file="study_data_for_analysis.csv")
```

This creates `study_data_for_analysis.csv` with one row per participant, ready for:
- Paired t-tests (Variant A vs. Variant B)
- SPSS / R / Python analysis
- Hypothesis testing

---

## 📝 Task Case Allocation

### **Variant A (Static):**
- Task 1: `high_risk_1` (P = 21.9%)
- Task 2: `medium_risk_4` (P = 38.0%)
- Task 3: `low_risk_7` (P = 60%+)

### **Variant B (Progressive):**
- Task 1: `high_risk_2` (P = 18.4%)
- Task 2: `medium_risk_5` (P = 39.0%)
- Task 3: `low_risk_8` (P = 76.6%)

**Balanced design:** Both variants have 1 high, 1 medium, 1 low risk case.

---

## ⚠️ Important Notes

1. **Participant ID is auto-generated** (P001, P002, ...) - no manual entry needed
2. **All responses auto-save** immediately - no manual data entry
3. **Session state persists** across phases for same participant
4. **One participant at a time** (in-person study, researcher-moderated)
5. **No internet required** (runs locally)

---

## 🎓 For Researcher

### **Quick Reference:**

| Phase | Command | Duration |
|-------|---------|----------|
| Variant A | `streamlit run interfaces/variant_a_static/app_with_study.py` | 10-12 min |
| Variant B | `streamlit run interfaces/variant_b_progressive/app_with_study.py` | 12-15 min |
| Final Feedback | `streamlit run interfaces/final_feedback_app.py` | 3-5 min |
| **Total** | | **25-32 min** |

### **Expected Data:**

- **Target:** 40 participants
- **Total sessions:** 40 × 3 apps = 120 sessions
- **Total data points:** 40 participants × 15 rows = 600 rows across all CSVs

---

## ✨ Advantages of This System

✅ **Zero manual data entry** - everything auto-logged  
✅ **No transcription errors** - direct CSV write  
✅ **Instant validation** - can't skip required fields  
✅ **Progress tracking** - participants see progress bars  
✅ **Session continuity** - Participant ID flows across phases  
✅ **Timestamps** - automatic for all responses  
✅ **Ready for analysis** - structured CSV format  

---

**Good luck with data collection!** 🎉
