# Thesis Writing Notes

**Quick reference for writing your MPhil thesis chapters**

---

## Section 3.8: Ethical Considerations (Protected Attributes)

### Add this text:

To minimize potential algorithmic bias, protected demographic attributes (gender, age band, disability status, highest education level) were excluded from the predictive model. The model uses only course-related features: enrollment characteristics (credits studied, prior attempts), VLE engagement patterns (clicks, activity access, days active), and assessment performance (scores, completion rate on pre-cutoff assessments).

We acknowledge that this exclusion does not guarantee algorithmic fairness, as retained features may act as proxies for protected attributes (e.g., engagement patterns may correlate with disability status, regional indicators may correlate with socioeconomic background). A comprehensive fairness audit analyzing false negative rates and prediction disparities across demographic groups would require a dedicated study and is beyond the scope of this interface-focused evaluation. This limitation is noted as important future work.

The exclusion decision aligns with the study's primary objective: evaluating how explanation *presentation* affects user trust and understanding in educational decision-support contexts. Both experimental interface conditions use identical underlying predictions, ensuring that any observed differences in user outcomes (trust, understanding, decision confidence) can be attributed to the explanation design rather than to differences in model predictions or fairness characteristics.

---

## Section 3.4: Model Development - Key Points to Include

### Temporal Validity

"To ensure temporal validity, we enforced a prediction cutoff at day 42 (six weeks into the module). This cutoff occurs after the first Tutor-Marked Assignment (TMA) deadline (typically day 19-25), providing sufficient time for students to establish engagement patterns while remaining early enough for meaningful intervention. All features were engineered to use only information available before this cutoff:
- VLE engagement features aggregate clicks with date ≤ 42 only
- Assessment features include only assessments due by day 42
- Demographic features are known at enrollment

A complete temporal audit trail is maintained in `data/processed/leakage_audit.txt`, documenting the temporal window and justification for each feature."

### SHAP Verification

"SHAP (SHapley Additive exPlanations) values were computed using LinearExplainer from the shap library (Lundberg & Lee, 2017). We explicitly extracted SHAP values for the positive class (Success = 1) and verified the additivity property: Σ(SHAP_i) + E[f(X)] ≈ f(x) in log-odds space, with tolerance ε < 0.01. All test samples passed this verification."

### Calibration

"To ensure trustworthy probability estimates for participants, we applied Platt scaling calibration using 5-fold cross-validation on the training set. Calibration quality was assessed via reliability diagrams and Brier score (uncalibrated: 0.1984, calibrated: 0.1975). The calibrated model was used in both interface variants to ensure participants received accurate confidence estimates."

---

## Section 3.7: Results - Performance Metrics

### Model Performance Table

| Metric | Value | Note |
|--------|-------|------|
| Test Accuracy | 68.03% | Day-42 early prediction |
| Precision | 0.73 (At-Risk), 0.64 (Success) | |
| Recall | 0.64 (At-Risk), 0.73 (Success) | |
| F1-Score | 0.68 (both classes) | |
| ROC-AUC | 0.7658 | Good discrimination |
| 5-Fold CV ROC-AUC | 0.7571 ± 0.0053 | Stable performance |
| Brier Score | 0.1975 | Well-calibrated |

**Note:** These metrics represent genuine early-prediction performance (day 42 cutoff) and are lower than commonly reported OULAD results that use post-hoc information. The performance drop from our initial leakage-inflated results (87.3% → 68.03%) confirms the temporal validity of the revised implementation.

---

## Figures to Include

### Figure: Calibration Reliability Diagrams (Before & After)
- **File (Uncalibrated):** `results/calibration_reliability_diagram_uncalibrated.png`
- **File (Calibrated):** `results/calibration_reliability_diagram_calibrated.png`
- **Caption:** "Reliability diagrams showing calibration improvement. (a) Uncalibrated model (Brier = 0.1984). (b) After Platt scaling (Brier = 0.1975). Calibrated probabilities align more closely with perfect calibration line, improving trustworthiness of confidence estimates shown to participants."
- **Usage:** Include both in Appendix, or just calibrated version in main Methodology section

### Figure: SHAP Feature Importance
- **File:** `results/shap_feature_importance.png`
- **Caption:** "Mean absolute SHAP values across all test samples, showing relative feature importance. Days since last activity is the strongest predictor of student success, followed by demographic factors (studied credits) and engagement patterns (days active, assessment scores)."
- **Usage:** Include in Methodology section (Chapter 3) to show which features drive model predictions

Complete ranking (all 11 features):
1. days_since_last_activity: 0.4216
2. studied_credits: 0.2632
3. days_active: 0.2431
4. avg_assessment_score: 0.2133
5. total_clicks_pre_cutoff: 0.1608
6. num_of_prev_attempts: 0.0723
7. num_assessments_completed: 0.0717
8. completion_rate: 0.0660
9. avg_clicks_per_active_day: 0.0529
10. num_activities_accessed: 0.0201
11. num_assessments_due: 0.0185

---

## Appendices

### Appendix A: Temporal Leakage Audit (Excerpt)
Copy first 20 lines from `data/processed/leakage_audit.txt`

### Appendix B: SHAP Additivity Verification
Include console output showing:
```
Sample 0: SHAP sum= -1.173, Model= -1.173, Diff=0.0000 ✓ PASS
Sample 1: SHAP sum= -0.248, Model= -0.248, Diff=0.0000 ✓ PASS
...
```

### Appendix C: Study Task Cases
Table with columns: Case ID, Risk Category, Prediction, True Outcome, Justification
From `study_task_cases.json`

---

## Discussion Points

### Limitations

**Temporal Prediction:**
"While our day-42 cutoff ensures temporal validity, it limits prediction accuracy compared to post-hoc analysis. This trade-off is inherent to genuine early-warning systems and reflects real-world constraints."

**Protected Attributes:**
"Excluding protected attributes reduces direct bias but does not eliminate proxy effects. Future work should conduct comprehensive fairness audits across demographic groups."

**Generalizability:**
"Results are specific to the OULAD dataset and UK Open University context. Validation in other educational settings is needed."

### Contributions

1. **Methodologically Rigorous Implementation:** First OULAD-based study with documented temporal leakage prevention and SHAP verification
2. **Interface Design Comparison:** Evidence-based comparison of static vs. progressive disclosure for ML explanations in educational contexts
3. **Replicable Framework:** Open implementation with automated tests enables future research

---

## Defense Preparation

### Expected Questions & Answers

**Q: How do you know there's no data leakage?**
A: "Every feature is documented in our leakage audit with its temporal window. The 19% performance drop when we enforced the day-42 cutoff proves the original implementation had leakage. Our automated tests verify the audit exists."

**Q: How do you verify SHAP correctness?**
A: "We verify the additivity property: sum of SHAP values plus expected value equals model output in log-odds space, with tolerance less than 0.01. All test samples pass. For single-instance predictions, we use a zero-vector background (representing the mean student after StandardScaling) to ensure meaningful SHAP values. We also have a single source-of-truth function for direction interpretation that both interfaces use."

**Q: Why are there two different SHAP expected values (-0.1981 vs -0.0698)?**
A: "Both are correct. SHAP expected value = E[f(X)] = average model output on the background dataset. Training evaluation uses 100-sample subsample of X_train as background (-0.1981), while interface predictions use a zero-vector background representing the mean student (-0.0698). Different backgrounds yield different expected values, but additivity holds in both contexts. This is standard SHAP behavior, not an error."

**Q: Why exclude protected attributes instead of auditing fairness?**
A: "Given our focus on interface evaluation rather than model fairness, exclusion provides simpler ethical compliance. We acknowledge this doesn't guarantee fairness and note comprehensive fairness auditing as important future work."

**Q: Can I reproduce your results?**
A: "Yes. Random seeds are fixed, dependencies are pinned, and we have 22 automated tests. The entire pipeline is documented and tested."

---

## Statistical Analysis (After Study)

### For Results Chapter

Use `study_response_logger.py` to collect data, then run the hypothesis tests:

```bash
# 1. Export for analysis
python -c "from study_response_logger import export_for_analysis; export_for_analysis()"

# 2. Run hypothesis tests (matches your proposal H1-H4)
python run_hypothesis_tests.py
```

The script tests all four hypotheses from your proposal:
- **H1:** Understanding ↔ Trust correlation (Pearson/Spearman)
- **H2:** Progressive > Static for Usability (SUS) - Paired t-test/Wilcoxon
- **H3:** Progressive > Static for Decision Confidence - Paired t-test/Wilcoxon  
- **H4:** Progressive > Static for Trust - Paired t-test/Wilcoxon

Report in Results chapter:
- Descriptive statistics: Mean ± SD for each measure per condition
- Test results: t-statistic/W-statistic, df, p-value
- Effect sizes: Cohen's d for paired comparisons, r for correlations
- Significance level: α = 0.05

**Note:** The script automatically chooses parametric (t-test, Pearson) or non-parametric (Wilcoxon, Spearman) tests based on Shapiro-Wilk normality checks, matching your proposal's statistical plan.

---

## Qualitative Data Analysis

### Section F: Additional Feedback (Collected at End of Session)

After both conditions, participants answer 4 open-ended questions:
1. What did you find most useful about the system?
2. What challenges did you experience while using the system?
3. How can the explanation interface be improved?
4. Which interface did you prefer (Static / Progressive) and why?

**Data file:** `study_data/qualitative_feedback.csv`

### Analysis Approach

Use thematic analysis (Braun & Clarke, 2006) to identify patterns:

**Steps:**
1. **Familiarization** - Read all responses multiple times
2. **Initial coding** - Identify interesting features, code systematically
3. **Theme generation** - Group codes into potential themes
4. **Theme review** - Check themes work with coded extracts
5. **Define themes** - Refine names and definitions
6. **Write-up** - Select compelling examples for each theme

### For Thesis Results Chapter

**Quantitative section:**
- Report H1-H4 statistical test results
- Include descriptive statistics table
- Report interface preference percentages from Q4

**Qualitative section:**
- Present themes identified from open-ended responses (Q1-Q3)
- Support each theme with participant quotes
- Link themes to quantitative findings where relevant
- Report preference reasons (Q4) to explain preference patterns

**Example structure:**
```
4.2 Qualitative Findings

Three main themes emerged from the open-ended feedback:

Theme 1: Value of Visual Explanations
Participants appreciated seeing visual representations of feature contributions.
P005 noted: "The bar charts made it easy to see which factors mattered most."

Theme 2: Need for Domain Context
Several participants wanted more context about what features meant...
```

---

## Quick Reference

**Files needed for thesis:**
- ✓ `results/calibration_reliability_diagram_uncalibrated.png`
- ✓ `results/calibration_reliability_diagram_calibrated.png`
- ✓ `results/shap_feature_importance.png`
- ✓ `data/processed/leakage_audit.txt`
- ✓ `study_task_cases.json`
- ✓ `results/shap_verification_output.txt`
- ✓ `results/model_training_output.txt` (complete)
- ✓ Study data CSVs (after data collection)

**Key numbers to remember:**
- Accuracy: **68.03%**
- ROC-AUC: **0.7658**
- Brier (uncalibrated): **0.1984**
- Brier (calibrated): **0.1975**
- Calibration improvement: **0.0009**
- Temporal cutoff: **Day 42**
- Random seed: **42**
- Test coverage: **22/22 PASS**

**Implementation milestones:**
- Initial model (with leakage): 87.3% accuracy
- After leakage fix: 68.03% accuracy (performance drop proves fix worked)
- Critical bugs fixed Sept 20, 2026: SHAP background + calibration diagrams
- Final feature set: 11 features (protected attributes excluded)
