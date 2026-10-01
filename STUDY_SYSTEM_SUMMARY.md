# Study System Summary

## What's Ready

Your **digital questionnaire system** is complete and ready for data collection.

---

## To Run a Study Session

```powershell
# 1. Variant A (10-12 min)
streamlit run interfaces/variant_a_static/app_with_study.py

# 2. Variant B (12-15 min)
streamlit run interfaces/variant_b_progressive/app_with_study.py

# 3. Final Feedback (3-5 min)
streamlit run interfaces/final_feedback_app.py
```

---

## What Gets Logged Automatically

All responses saved to `study_data/`:
- Demographics (Section A: 7 questions)
- Decision Confidence (Section E: 4 items × 6 tasks)
- SUS (Section B: 10 items × 2 variants)
- Trust (Section C: 5 items × 2 variants)
- Understanding (Section D: 5 items × 2 variants)
- Qualitative Feedback (Section F: 4 open-ended)

**Total: 15 CSV rows per participant**

---

## 🎯 Key Features

✅ Auto participant ID (P001, P002, P003...)  
✅ Pre-filled task cases (no manual data entry)  
✅ Automatic CSV logging (zero transcription)  
✅ Form validation (required fields enforced)  
✅ Session continuity (ID flows across apps)  
✅ Progress tracking (visual progress bars)  

---

## Full Instructions

See **[STUDY_INSTRUCTIONS.md](STUDY_INSTRUCTIONS.md)** for complete details.

---

## Test Before First Participant

Run through all 3 apps yourself to verify everything works, then delete test data:

```powershell
Remove-Item -Recurse study_data
```

---

**That's it! Your study is ready to launch.** 
