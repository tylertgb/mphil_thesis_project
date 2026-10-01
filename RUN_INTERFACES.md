# How to Run the System - Quick Guide

## Two Ways to Use the System

1. **For User Study Data Collection** → Use `app_with_study.py` (integrated questionnaires)
2. **For Testing/Demo** → Use `app.py` (interfaces only)

See sections below for details.

---

## Prerequisites

Make sure you have installed dependencies:
```bash
pip install -r requirements.txt
```

---

## Running the Interfaces

### Option 1: Run Variant A (Static Explanation)

```bash
streamlit run interfaces/variant_a_static/app.py
```

**What you'll see:**
- Full SHAP bar chart shown immediately
- All feature attributions visible at once
- Prediction + probability + risk category
- Complete explanation up front

**Access at:** http://localhost:8501

---

### Option 2: Run Variant B (Progressive Disclosure)

```bash
streamlit run interfaces/variant_b_progressive/app.py
```

**What you'll see:**
- **Layer 1:** Prediction + risk category only
- **Layer 2:** Top 3 contributing features (expand to see)
- **Layer 3:** Full SHAP bar chart (expand further)
- Progressive revelation of complexity

**Access at:** http://localhost:8501

---

## Testing the Interface

### Step 1: Fill in Student Information

The form includes:
- **Student Background:**
  - Studied Credits (60/120/180/240/300/360)
  - Number of Previous Attempts (0-3+)

- **Assessment Performance (by Day 42):**
  - Average Assessment Score (0-100)
  - Number Completed / Number Due
  - Completion Rate (auto-calculated)

- **VLE Engagement (before Day 42):**
  - Total Clicks
  - Number of Activities Accessed
  - Days Active
  - Average Clicks per Active Day
  - Days Since Last Activity

### Step 2: Click "Predict Student Outcome"

The system will:
1. Load the trained model
2. Compute SHAP explanations
3. Display prediction with explanations
4. Show risk category (At-Risk ▲ or Success ●)

### Step 3: Try Different Students

**Pre-built cases available in:** `study_task_cases.json`

Example high-risk student:
- studied_credits: 120
- num_of_prev_attempts: 0
- avg_assessment_score: 69
- num_assessments_completed: 1
- num_assessments_due: 2
- completion_rate: 0.5
- total_clicks_pre_cutoff: 92
- num_activities_accessed: 14
- days_active: 10
- avg_clicks_per_active_day: 9.2
- days_since_last_activity: 5

**Expected:** At-Risk prediction (~22% success probability)

---

## For Study Data Collection

**NEW: Integrated Study Apps with Digital Questionnaires**

The study now has dedicated apps with built-in questionnaires that automatically log all responses:

### 1. Run Study Session (3 Apps)

```bash
# Step 1: Variant A with integrated questionnaires (10-12 min)
streamlit run interfaces/variant_a_static/app_with_study.py

# Step 2: Variant B with integrated questionnaires (12-15 min)
streamlit run interfaces/variant_b_progressive/app_with_study.py

# Step 3: Final qualitative feedback (3-5 min)
streamlit run interfaces/final_feedback_app.py
```

**Features:**
- ✅ Auto participant ID generation (P001, P002...)
- ✅ Pre-filled task cases (no manual data entry)
- ✅ All questionnaires integrated (Demographics, SUS, Trust, Understanding, Decision Confidence)
- ✅ Automatic CSV logging (all responses saved instantly)
- ✅ Session state continuity (ID flows across apps)

**See [STUDY_INSTRUCTIONS.md](STUDY_INSTRUCTIONS.md) for complete study guide.**

### 2. Manual Data Collection (Old Method)

If you need to test interfaces standalone without questionnaires:

```bash
# Run basic interfaces for testing
streamlit run interfaces/variant_a_static/app.py
streamlit run interfaces/variant_b_progressive/app.py
```

Then manually log responses using:
```python
from study_response_logger import StudyResponseLogger
logger = StudyResponseLogger('study_data')
logger.log_sus('P001', 'variant_a', [4,2,5,2,4,1,4,2,5,1])
# ... etc
```

### 3. Export for Analysis
```bash
python -c "from study_response_logger import export_for_analysis; export_for_analysis()"
python run_hypothesis_tests.py
```

---

## Stopping the Interface

Press `Ctrl+C` in the terminal where Streamlit is running.

---

## Troubleshooting

**Interface won't start:**
- Check if port 8501 is already in use
- Try: `streamlit run interfaces/variant_a_static/app.py --server.port 8502`

**Model not found error:**
- Run: `python models/logistic_regression_model.py`
- This trains the model and saves artifacts

**Import errors:**
- Run: `pip install -r requirements.txt`
- Make sure you're in the project root directory

---

## Comparing Both Interfaces

To see the difference side-by-side:

1. Run Variant A in one terminal (port 8501)
2. Run Variant B in another terminal with different port:
   ```bash
   streamlit run interfaces/variant_b_progressive/app.py --server.port 8502
   ```
3. Open both in browser tabs
4. Enter the same student data in both
5. Compare how explanations are presented

**Key Difference:** Same underlying prediction and SHAP values, different presentation.

---

## Quick Demo

Want to see it immediately? Run:

```bash
streamlit run interfaces/variant_b_progressive/app.py
```

Then enter this high-risk student:
- Credits: 120, Attempts: 0
- Assessment: 69% average, 1/2 completed
- VLE: 92 clicks, 14 activities, 10 days active
- Last activity: 5 days ago

Watch how the progressive interface reveals information in layers!
