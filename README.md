# MPhil Thesis: SHAP-Based Explainable Interfaces for Educational Risk Prediction

**A Human-Centered Evaluation of SHAP-Based Explainable Interfaces for Logistic Regression Models in Educational Decision-Support Systems**

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Model Pipeline
```bash
# Generate leakage-free dataset
python preprocessing_v2.py

# Train calibrated model with SHAP verification
python models/logistic_regression_model.py

# Run automated tests (22 tests should all PASS)
python tests/test_model_integrity.py
python tests/test_interface_consistency.py
```

### 3. Generate Study Materials
```bash
# Generate task cases for user study
python generate_study_task_cases.py

# See example logging usage
python study_response_logger.py
```

### 4. Run Interfaces (for study or demo)
```bash
# Variant A - Static Explanation
streamlit run interfaces/variant_a_static/app.py

# Variant B - Progressive Disclosure  
streamlit run interfaces/variant_b_progressive/app.py
```

---

## Key Implementation Details

### Temporal Leakage Fix
- **Prediction cutoff:** Day 42 (6 weeks into module)
- **Why:** After first TMA, early enough for intervention
- **VLE features:** Only clicks with `date <= 42`
- **Assessment features:** Only assessments due by day 42
- **Documentation:** See `data/processed/leakage_audit.txt`

### Model Performance (Post-Fix)
- **Accuracy:** 68.03% (realistic for early prediction)
- **ROC-AUC:** 0.7658
- **Brier Score:** 0.1975 (calibrated)
- **Performance drop:** 87% → 68% (proves leakage was fixed)

### SHAP Implementation
- **Sign convention:** Positive = toward Success, Negative = toward At-Risk
- **Verification:** Additivity checked (all samples pass, ε < 0.01)
- **Single source of truth:** `get_shap_direction()` function
- **Background:** Training set mean (after standardization)

### Calibration
- **Method:** Platt scaling via `CalibratedClassifierCV`
- **Improvement:** Brier 0.1984 → 0.1975
- **Artifact:** `results/calibration_reliability_diagram.png`
- **Usage:** Both interfaces use `calibrated_model.pkl`

### Protected Attributes
- **Decision:** Excluded (Option A)
- **Rationale:** Minimize direct bias, simpler ethics review
- **Excluded:** gender, age_band, disability, highest_education
- **Limitation:** Proxy features may still exist

### Test Coverage
- **Model Integrity:** 15 tests (leakage, SHAP, calibration, seeds)
- **Interface Consistency:** 7 tests (predictions, SHAP, PII)
- **Status:** 22/22 PASS (100%)

---

## Project Structure

```
├── data/
│   ├── raw/                    # Original OULAD data
│   └── processed/              # Leakage-free dataset + audit
├── models/
│   ├── logistic_regression_model.py  # Main model with all fixes
│   └── saved_models/           # Trained artifacts (incl. calibrated)
├── interfaces/
│   ├── variant_a_static/       # Static explanation interface
│   ├── variant_b_progressive/  # Progressive disclosure interface
│   └── shared_components/      # Shared form and encoders
├── tests/
│   ├── test_model_integrity.py      # 15 tests
│   └── test_interface_consistency.py # 7 tests
├── preprocessing_v2.py         # Leakage-free preprocessing
├── generate_study_task_cases.py     # Task case generator
├── study_response_logger.py         # Study data collection
└── requirements.txt            # Pinned dependencies
```

---

## For Your Thesis

### Key Files to Reference

**Methodology Chapter:**
- `data/processed/leakage_audit.txt` - Temporal constraint documentation
- `results/calibration_reliability_diagram.png` - Calibration figure
- `results/calibration_report.txt` - Brier scores

**Appendices:**
- `study_task_cases.json` - Task cases with justifications
- Model training console output - SHAP additivity verification

**Proposal Update:**
- See `THESIS_NOTES.md` for Section 3.8 text on protected attributes

### Performance to Report

| Metric | Pre-Fix (Leakage) | Post-Fix | Note |
|--------|-------------------|----------|------|
| Accuracy | ~87% | 68.03% | Drop proves fix worked |
| ROC-AUC | ~0.92 | 0.7658 | Realistic for early prediction |
| Brier | - | 0.1975 | Calibrated probabilities |

---

## Reproducibility

- **Python:** 3.12.1
- **Random seed:** 42 (fixed throughout)
- **Dependencies:** Pinned in `requirements.txt`
- **Tests:** Run before any thesis claims

---

## Contact & Support

**For examiners:**
- All code is documented with inline comments
- 22 automated tests verify correctness
- Implementation matches proposal Section 3.4-3.8

**For future students:**
- Start with this README
- Run tests first to verify setup
- See `THESIS_NOTES.md` for thesis-specific guidance
