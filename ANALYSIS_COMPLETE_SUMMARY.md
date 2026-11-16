# MPhil Thesis Analysis — Complete Summary (Corrected)

**Date:** November 15, 2026
**Final Sample:** n = 31 (complete paired data)
**Study Design:** Counterbalanced within-subjects design
- Group AB (n=16): Static first → Progressive second
- Group BA (n=15): Progressive first → Static second
- **Confirmed by timestamps:** All 31 participants match their assigned order (31/31 ✅)
**Analysis spec:** `analysis_spec_for_kiro.md` (all tests specified in advance)

---

## ⚠️ CORRECTIONS FROM PREVIOUS VERSION

| Item | Previous Claim | Corrected Finding | Evidence |
|------|---------------|-------------------|----------|
| H2 p-value | p=.002 (ANOVA p used) | **p=.0015** (paired t-test, primary test) | `run_full_analysis_updated.py` |
| H3 p-value | p=.013 (ANOVA p used) | **p=.0115** | Same |
| H4 p-value | p=.015 (ANOVA p used) | **p=.0140** | Same |
| Holm H2 | p=.006 | **p=.0046** | Same |
| Holm H3 | p=.026 | **p=.023** | Same |
| Holm H4 | p=.026 | **p=.023** | Same |
| Preference | 83.9% (26/31) Progressive | **93.5% (29/31) Progressive** | Current `qualitative_feedback.csv` |
| Preference by group | "Both Static-preferring in BA" | **AB: 15 Progressive, 1 Static; BA: 14 Progressive, 1 Static** | Same |
| Order effects language | "Confirms no order effects" | **"No evidence of order effects"** (groups of 16 and 15 are small) | Statistical caution |
| H1 explanation | "r=.799 was order artefact" | **Origin of old r=.799 unknown — cannot be reproduced from current data** | `investigate_h1_flip.py` |
| Counterbalancing | Previously questioned | **Confirmed real: 31/31 timestamps match assignments** | `verify_all_assignments.py` |

---

## ✅ COMPLETED ANALYSES

### 1. Sample Composition (Table 4.1)
**File:** `results/tables/table_4_1_sample_composition.csv`

| Characteristic | n | % |
|---|---|---|
| Age 18–29 | 7 | 22.6% |
| Age 30–39 | 13 | 41.9% |
| Age 40–49 | 8 | 25.8% |
| Age 50–59 | 3 | 9.7% |
| Male | 25 | 80.6% |
| Female | 6 | 19.4% |
| Master's degree | 26 | 83.9% |
| Doctoral degree | 5 | 16.1% |
| Analytics familiarity (Yes) | 16 | 51.6% |
| Analytics familiarity (No) | 15 | 48.4% |
| Experience 0–10 years | 27 | 87.1% |
| **Counterbalancing: AB** | **16** | **51.6%** |
| **Counterbalancing: BA** | **15** | **48.4%** |
| **Balance (χ²=0.032, p=.858)** | — | **Well balanced** |

---

### 2. Reliability Analysis (Cronbach's α)
**File:** `results/tables/reliability_cronbach_alpha.csv`

| Scale | α (Static) | α (Progressive) | Interpretation |
|-------|-----------|----------------|----------------|
| SUS | .811 | .837 | Good |
| Trust | .791 | .911 | Good → Excellent |
| Understanding | .938 | .943 | Excellent |
| Decision Confidence | .881 | .901 | Good → Excellent |

Note: Trust, Understanding, and Confidence are not validated instruments; α estimates are approximate at n=31.

---

### 3. Descriptive Statistics (Table 4.2)

| Measure | Static M (SD) | Progressive M (SD) | Mean Diff | 95% CI |
|---------|-------------|-------------------|-----------|--------|
| SUS (0–100) | 62.58 (7.62) | 68.47 (5.83) | +5.89 | [2.44, 9.34] |
| Trust (1–5) | 3.81 (0.35) | 4.07 (0.35) | +0.25 | [0.06, 0.45] |
| Understanding (1–5) | 3.73 (0.41) | 3.88 (0.63) | +0.16 | [−0.14, 0.45] |
| Decision Confidence (1–5) | 4.01 (0.25) | 4.17 (0.20) | +0.16 | [0.04, 0.28] |

---

### 4. Hypothesis Testing Results (Table 4.3)
**Files:**
- `results/updated_analysis/table_4_3_hypothesis_results.csv`
- `run_full_analysis_updated.py` (fully reproducible, seed 42)

**Multiplicity rule (specified in advance):** Holm correction applied to H2–H4.
A hypothesis is supported only if Holm-adjusted p < .05 AND mean difference is in the predicted direction.
**Primary test for H2–H4:** Paired t-test (all difference distributions normal by Shapiro-Wilk).

---

#### H1: Understanding ↔ Trust (Positive Association)
**Test:** Spearman ρ on participant-average scores
(Understanding averages non-normal: W=0.952, p=.017; Trust averages normal: W=0.971, p=.519 → Spearman used)

| Analysis | Statistic | p | 95% CI |
|----------|-----------|---|--------|
| Primary (participant averages, n=31) | ρ = .037 | .844 | [−.339, .393] |
| Sensitivity: rm_corr (n=62 obs) | r = .216 | .234 | [−.140, .530] |
| Sensitivity: Static only (n=31) | r = .118 | .529 | — |
| Sensitivity: Progressive only (n=31) | r = .097 | .606 | — |

**Result: ❌ NOT SUPPORTED**

No significant association between Understanding and Trust was found in the counterbalanced dataset. All four analyses converge near zero. The origin of the previously reported r=.799 cannot be reproduced from current data and should not be cited.

---

#### H2: Progressive Interface Improves Usability (SUS)
**Normality of differences:** W=0.936, p=.063 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 62.58 (7.62) | 68.47 (5.83) | +5.89 (9.43) |

- **Paired t-test:** t(30) = 3.483, p = .0015
- **Mixed ANOVA (interface effect):** F(1,29) = 11.729, p = .002, η²p = .288
- **Holm-adjusted p:** .0046
- **Effect size:** dz = 0.626 (medium-large)
- **95% CI on difference:** [2.44, 9.34]
- **Interface × Order interaction:** F(1,29) = 0.004, p = .950 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.0015, Holm p=.0046, correct direction)

Progressive interface was rated significantly more usable with a medium-large effect. The 5.9-point advantage exceeds the commonly cited 3.5-point "noticeable difference" threshold, though the lower CI bound (2.44) is close to it — interpret conservatively. Effect was consistent across both order groups (AB diff=+5.78, BA diff=+6.00), and the Interface × Order interaction was non-significant, confirming the finding is not an order artefact.

---

#### H3: Progressive Interface Increases Decision Confidence
**Normality of differences:** W=0.979, p=.785 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 4.01 (0.25) | 4.17 (0.20) | +0.16 (0.33) |

- **Paired t-test:** t(30) = 2.692, p = .0115
- **Mixed ANOVA (interface effect):** F(1,29) = 7.012, p = .013, η²p = .195
- **Holm-adjusted p:** .023
- **Effect size:** dz = 0.484 (medium)
- **95% CI on difference:** [0.04, 0.28]
- **Interface × Order interaction:** F(1,29) = 0.017, p = .897 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.0115, Holm p=.023, correct direction)

**Ceiling effect note:** Both condition means exceed 4.0 on a 1–5 scale (SD ≈ 0.2–0.25). The scale is near its upper limit, which compresses the observable difference. Mention this when interpreting H3 in the thesis.

---

#### H4: Progressive Interface Increases Trust
**Normality of differences:** W=0.952, p=.172 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 3.81 (0.35) | 4.07 (0.35) | +0.25 (0.54) |

- **Paired t-test:** t(30) = 2.611, p = .0140
- **Mixed ANOVA (interface effect):** F(1,29) = 6.684, p = .015, η²p = .187
- **Holm-adjusted p:** .023
- **Effect size:** dz = 0.469 (medium)
- **95% CI on difference:** [0.06, 0.45]
- **Interface × Order interaction:** F(1,29) = 0.418, p = .523 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.0140, Holm p=.023, correct direction)

Effect consistent across order groups (AB diff=+0.31, BA diff=+0.19). Non-significant interaction confirms the finding is not driven by order.

---

### 5. Overall Hypothesis Summary

| H | Hypothesis | Test | Statistic | p (raw) | p (Holm) | Effect | Supported |
|---|-----------|------|-----------|---------|----------|--------|-----------|
| H1 | Understanding ↔ Trust | Spearman ρ | ρ=.037 | .844 | N/A | ρ=.037 | ❌ No |
| H2 | Progressive > Static: SUS | Paired t-test | t(30)=3.483 | .0015 | .0046 | dz=.626 | ✅ Yes |
| H3 | Progressive > Static: Confidence | Paired t-test | t(30)=2.692 | .0115 | .023 | dz=.484 | ✅ Yes |
| H4 | Progressive > Static: Trust | Paired t-test | t(30)=2.611 | .0140 | .023 | dz=.469 | ✅ Yes |

**Overall: 3/4 hypotheses supported**

---

### 6. Counterbalancing & Order Effects
**File:** `results/updated_analysis/order_period_effect.csv`
**Timestamp verification:** `verify_all_assignments.py` — 31/31 ✅

| Measure | AB diff M (SD) | BA diff M (SD) | t | p | Conclusion |
|---------|--------------|--------------|---|---|------------|
| SUS | +5.78 (9.65) | +6.00 (9.49) | −0.064 | .950 | No evidence of order effect |
| Confidence | +0.15 (0.28) | +0.17 (0.39) | −0.130 | .897 | No evidence of order effect |
| Trust | +0.31 (0.53) | +0.19 (0.56) | 0.646 | .523 | No evidence of order effect |
| Understanding | +0.33 (0.42) | −0.03 (1.11) | 1.179 | .248 | No evidence of order effect |

No significant order effects found for any measure. Note: with groups of n=16 and n=15, these tests have limited power to detect small order effects. Describe as "no evidence of order effects" rather than "order effects ruled out."

The progressive interface advantage on SUS, Trust, and Confidence was consistent regardless of which interface participants saw first. All Interface × Order interactions were non-significant.

---

### 7. Perceived Understanding (Additional)
**Mixed ANOVA:** F(1,29)=1.079, p=.308, η²p=.036, dz=.185
**Normality of differences:** W=0.759, p<.001 — non-normal

Understanding showed a small, non-significant difference between interfaces. The near-zero correlations with Trust (H1) across all sensitivity analyses suggest Understanding and Trust operate independently in this sample. Report descriptively as an exploratory finding.

---

### 8. Preference Analysis
**File:** `results/tables/preference_analysis.csv`

- **93.5% (29/31) preferred Progressive (Variant B)**
- **6.5% (2/31) preferred Static (Variant A)**

| Order group | n | Progressive | Static |
|---|---|---|---|
| AB (Static first) | 16 | 15 (93.8%) | 1 (6.3%) |
| BA (Progressive first) | 15 | 14 (93.3%) | 1 (6.7%) |

The near-identical preference rates across both order groups (93.8% vs 93.3%) are noteworthy. BA participants saw Progressive **first** and 14/15 still preferred it — this rules out a simple recency explanation (preferring whichever was seen last). AB participants saw Progressive **second** and 15/16 preferred it. The convergence across both orders strengthens the preference finding.

**Appropriate thesis language:**
> "29 of 31 participants (93.5%) preferred the Progressive interface. Preference rates were near-identical across order groups (AB: 93.8%, BA: 93.3%), suggesting the preference was not driven by recency effects."

---

### 9. Qualitative Data
**Files:** `results/qualitative/`

- 31 participants, 100% response rate on Q1 and Q4
- Q2 (Challenges): 90.3% responded
- Q3 (Improvements): 96.8% responded
- Thematic coding must be completed manually by the researcher (Braun & Clarke, 2006)

**Themes visible in raw data:**
- Q1: SHAP explanation clarity, factor visibility, confidence scores
- Q2: Technical terminology, colour scheme, slow navigation
- Q3: Export functionality, trend lines, mobile version, glossary
- Q4: 93.5% Progressive — reasons centre on transparency and explanation quality

---

## 📊 LANGUAGE FOR THESIS CHAPTERS

### Chapter 3 (Methods) — correct wording
> "To control for order effects, participants were randomly assigned to one of two presentation orders based on enrolment timestamp: Group AB (n=16) completed the Static interface first, followed by the Progressive interface; Group BA (n=15) completed the Progressive interface first, followed by the Static interface. This counterbalanced within-subjects design allows the interface effect to be estimated independently of presentation order. Assignment was confirmed from response timestamps (31/31 participants matched their assigned order)."

### Chapter 4 (Results) — reporting templates

**H2:**
> "A paired t-test indicated that Progressive interface usability (M=68.47, SD=5.83) was significantly higher than Static interface usability (M=62.58, SD=7.62), t(30)=3.483, p=.0015, dz=0.626, 95% CI [2.44, 9.34], Holm p=.005. A 2×2 mixed ANOVA confirmed the interface effect, F(1,29)=11.729, p=.002, η²p=.288, with no significant Interface × Order interaction, F(1,29)=0.004, p=.950, indicating the advantage was consistent across presentation orders."

**H3:**
> "Decision confidence was significantly higher under the Progressive interface (M=4.17, SD=0.20) than the Static interface (M=4.01, SD=0.25), t(30)=2.692, p=.012, dz=0.484, 95% CI [0.04, 0.28], Holm p=.023. Note that both means fall near the ceiling of the scale (>4.0 on a 1–5 scale), which may limit the detectable range of differences."

**H4:**
> "Trust was significantly higher under the Progressive interface (M=4.07, SD=0.35) than the Static interface (M=3.81, SD=0.35), t(30)=2.611, p=.014, dz=0.469, 95% CI [0.06, 0.45], Holm p=.023. The Interface × Order interaction was non-significant, F(1,29)=0.418, p=.523, confirming the effect was consistent regardless of presentation order."

**H1:**
> "No significant association was found between perceived understanding and trust, Spearman ρ=.037, p=.844, 95% CI [−.339, .393] (n=31 participant averages). Sensitivity analyses using repeated-measures correlation (r=.216, p=.234) and per-condition Pearson correlations (Static: r=.118, p=.529; Progressive: r=.097, p=.606) were consistent with this null finding."

### Chapter 5 (Discussion) — limitations to include
1. **Small sample, single institution.** n=31 from UDS/BACE limits generalisation beyond similar populations.
2. **Ceiling effects on Decision Confidence.** Both condition means exceed 4.0 (SD≈0.2). Limited scale range may underestimate the true effect.
3. **H1 not supported.** The absence of an Understanding–Trust correlation is inconsistent with theoretical expectations. Future work with larger samples and validated instruments should revisit this.
4. **Order effects test power.** With n=16 and n=15 per group, the order effects tests have limited power to detect small order effects. Absence of significance is not proof of absence.

---

## 📁 OUTPUT FILES

| File | Description | Status |
|------|-------------|--------|
| `results/figures/figure_4_1_paired_comparisons.png/.pdf` | Paired comparisons — updated ✅ | ✅ Use |
| `results/figures/figure_4_2_understanding_trust_correlation.png/.pdf` | Understanding–Trust scatter — updated ✅ | ✅ Use |
| `results/updated_analysis/table_4_3_hypothesis_results.csv` | Table 4.3 | ✅ Use (use paired t p-values) |
| `results/updated_analysis/order_period_effect.csv` | Order effects check | ✅ Use |
| `results/mixed_anova/mixed_anova_summary.csv` | Mixed ANOVA summary | ✅ Use (for interaction check) |
| `results/counterbalanced_analysis/*.png` | Interaction plots (4 DVs) | ✅ Use |
| `results/tables/table_4_1_sample_composition.csv` | Table 4.1 | ✅ Valid |
| `results/tables/table_4_2_descriptives.csv` | Table 4.2 | ✅ Valid |
| `results/tables/reliability_cronbach_alpha.csv` | Reliability | ✅ Valid |
| `results/tables/preference_analysis.csv` | Preference counts (29/31) | ✅ Valid |
| `results/appendix/appendix_a_normality_distributions.png/.pdf` | Appendix A | ✅ Valid |
| `results/appendix/appendix_b_qq_plots.png/.pdf` | Appendix B | ✅ Valid |
| `results/qualitative/` | Qualitative exports | ✅ Valid |

---

## 🔁 REPRODUCIBLE SCRIPTS

| Script | Purpose |
|--------|---------|
| `run_full_analysis_updated.py` | H1–H4, order effects, Table 4.3 (seed 42) |
| `run_mixed_anova.py` | Mixed ANOVA F-statistics, η²p |
| `analyze_counterbalanced_data.py` | Descriptives + interaction plots |
| `investigate_h1_flip.py` | H1 verification, true t p-values, preference counts |
| `verify_all_assignments.py` | Confirms 31/31 timestamp-assignment match |
| `calculate_reliability_cronbach_alpha.py` | Cronbach's α |
| `generate_table_4_1_sample_composition.py` | Table 4.1 demographics |

---

## 📝 REMAINING FOR RESEARCHER

1. **Write Chapter 4 Results** using tables and reporting templates above
2. **Update Chapter 3** to describe counterbalanced design and confirm assignment from timestamps
3. **Conduct thematic coding** (Braun & Clarke) on qualitative data — files in `results/qualitative/`
4. **Write Chapter 5 Discussion** using four limitations listed above
5. **Reconcile Appendix A** — confirm Understanding scale is 5 items as logged

---

## 🔒 DATA INTEGRITY

- **Clean dataset:** n=31, no missing paired data
- **Counterbalancing confirmed:** 31/31 timestamps match AB/BA assignments (`verify_all_assignments.py`)
- **Reproducible:** All analyses scripted with seed 42, version-controlled
- **Transparent:** Raw and Holm-adjusted p-values reported side by side; paired t-test used as primary (not ANOVA p)
- **Honest:** Non-significant H1, ceiling effects on Confidence, and order effect test limitations reported plainly
- **Corrected:** p-values now from paired t-test (primary); preference count corrected to 29/31 (93.5%)

---

**Analysis complete and ready for thesis writing.** 🎓
*Last updated: November 15, 2026 — post-investigation corrections applied*
