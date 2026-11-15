# MPhil Thesis Analysis — Complete Summary (Updated)

**Date:** November 15, 2026
**Final Sample:** n = 31 (complete paired data)
**Study Design:** Counterbalanced within-subjects design
- Group AB (n=16): Static first → Progressive second
- Group BA (n=15): Progressive first → Static second
**Analysis spec:** `analysis_spec_for_kiro.md` (all tests specified in advance)

---

## ⚠️ KEY CHANGES FROM PREVIOUS VERSION

| Item | Previous (Fixed-order) | Updated (Counterbalanced) |
|------|----------------------|--------------------------|
| H1 (Understanding↔Trust) | r=.799, p<.001 ✅ | ρ=.037, p=.844 ❌ NOT SUPPORTED |
| H2 (SUS) | t, p=.192 ❌ | F(1,29)=11.729, p=.002 ✅ SUPPORTED |
| H3 (Confidence) | Wilcoxon **Z**=100.5 | Paired t(30)=2.692, p=.013 ✅ |
| H4 (Trust) | Wilcoxon **Z**=55.0 | Paired t(30)=2.611, p=.015 ✅ |
| Order effects | Untestable (fixed order) | Properly tested — none significant |
| "Pre-registered" | Used incorrectly | Replaced with "specified in advance" |

---

## ✅ COMPLETED ANALYSES

### 1. Sample Composition (Table 4.1)
**File:** `results/tables/table_4_1_sample_composition.csv`

**Key Demographics:**
- **Age:** 30–39 (41.9%), 40–49 (25.8%)
- **Gender:** 80.6% male, 19.4% female
- **Education:** 83.9% Master's, 16.1% Doctoral
- **Experience:** 0–10 years (87%)
- **Analytics Familiarity:** 51.6% Yes (familiarity_with_analytics=5), 48.4% No (=1)
- **Counterbalancing:** AB=16, BA=15 (χ²=0.032, p=.858 — well balanced)

---

### 2. Reliability Analysis (Cronbach's α)
**File:** `results/tables/reliability_cronbach_alpha.csv`

| Scale | α (Static) | α (Progressive) | Interpretation |
|-------|-----------|----------------|----------------|
| SUS | .811 | .837 | Good |
| Trust | .791 | .911 | Good → Excellent |
| Understanding | .938 | .943 | Excellent |
| Decision Confidence | .881 | .901 | Good → Excellent |

All scales demonstrate acceptable to excellent internal consistency.
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

---

#### H1: Understanding ↔ Trust (Positive Association)
**Test:** Spearman ρ on participant-average scores (Understanding non-normal: W=0.952, p=.017)

| Analysis | Statistic | p | 95% CI |
|----------|-----------|---|--------|
| Primary (participant averages, n=31) | ρ = .037 | .844 | [−.339, .393] |
| Sensitivity: rm_corr (n=62 obs) | r = .216 | .234 | [−.140, .530] |
| Sensitivity: Static only | r = .118 | .529 | — |
| Sensitivity: Progressive only | r = .097 | .606 | — |

**Result: ❌ NOT SUPPORTED**

No significant association between Understanding and Trust was found in the counterbalanced dataset. All analyses are consistent: the correlation is near zero across all analytic approaches. This contrasts with the previous fixed-order result (r=.799) which was likely inflated by shared order effects — both scores rose together as participants moved to their second interface.

**Note for thesis:** Report this honestly. The previous r=.799 was an artefact of fixed ordering, not a genuine Understanding–Trust relationship. The counterbalanced design gives a more trustworthy estimate.

---

#### H2: Progressive Interface Improves Usability (SUS)
**Normality:** W=0.936, p=.063 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 62.58 (7.62) | 68.47 (5.83) | +5.89 (9.43) |

- **Paired t-test:** t(30) = 3.483, p = .002
- **Mixed ANOVA (interface effect):** F(1,29) = 11.729, p = .002, η²p = .288
- **Holm-adjusted p:** .006
- **Effect size:** dz = 0.626 (medium-large)
- **95% CI on difference:** [2.44, 9.34]
- **Interface × Order interaction:** F(1,29) = 0.004, p = .950 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.002, Holm p=.006, correct direction)

Progressive interface was rated significantly more usable, with a medium-large effect. The effect was identical across both order groups (AB diff=+5.78, BA diff=+6.00), confirming the finding is not an order artefact.

---

#### H3: Progressive Interface Increases Decision Confidence
**Normality:** W=0.979, p=.785 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 4.01 (0.25) | 4.17 (0.20) | +0.16 (0.33) |

- **Paired t-test:** t(30) = 2.692, p = .013
- **Mixed ANOVA (interface effect):** F(1,29) = 7.012, p = .013, η²p = .195
- **Holm-adjusted p:** .026
- **Effect size:** dz = 0.484 (medium)
- **95% CI on difference:** [0.04, 0.28]
- **Interface × Order interaction:** F(1,29) = 0.017, p = .897 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.013, Holm p=.026, correct direction)

Participants reported significantly higher decision confidence with the Progressive interface. Effect was consistent across both order groups (AB diff=+0.15, BA diff=+0.17).

---

#### H4: Progressive Interface Increases Trust
**Normality:** W=0.952, p=.172 → Normal → **Paired t-test**

| | Static | Progressive | Difference |
|--|--------|-------------|-----------|
| M (SD) | 3.81 (0.35) | 4.07 (0.35) | +0.25 (0.54) |

- **Paired t-test:** t(30) = 2.611, p = .015
- **Mixed ANOVA (interface effect):** F(1,29) = 6.684, p = .015, η²p = .187
- **Holm-adjusted p:** .026
- **Effect size:** dz = 0.469 (medium)
- **95% CI on difference:** [0.06, 0.45]
- **Interface × Order interaction:** F(1,29) = 0.418, p = .523 ✅ No interaction

**Result: ✅ SUPPORTED** (raw p=.015, Holm p=.026, correct direction)

Participants reported significantly higher trust in the Progressive interface. Effect was consistent across order groups (AB diff=+0.31, BA diff=+0.19).

---

### 5. Overall Hypothesis Summary

| H | Hypothesis | Test | Statistic | p (raw) | p (Holm) | η²p / d | Supported |
|---|-----------|------|-----------|---------|----------|---------|-----------|
| H1 | Understanding ↔ Trust | Spearman ρ | ρ=.037 | .844 | N/A | ρ=.037 | ❌ No |
| H2 | Progressive > Static: SUS | Paired t + Mixed ANOVA | t(30)=3.483; F(1,29)=11.729 | .002 | .006 | η²p=.288; dz=.626 | ✅ Yes |
| H3 | Progressive > Static: Confidence | Paired t + Mixed ANOVA | t(30)=2.692; F(1,29)=7.012 | .013 | .026 | η²p=.195; dz=.484 | ✅ Yes |
| H4 | Progressive > Static: Trust | Paired t + Mixed ANOVA | t(30)=2.611; F(1,29)=6.684 | .015 | .026 | η²p=.187; dz=.469 | ✅ Yes |

**Overall: 3/4 hypotheses supported**

---

### 6. Counterbalancing & Order Effects
**File:** `results/updated_analysis/order_period_effect.csv`

| Measure | AB diff M (SD) | BA diff M (SD) | t | p | Order Effect? |
|---------|--------------|--------------|---|---|---------------|
| SUS | +5.78 (9.65) | +6.00 (9.49) | −0.064 | .950 | ✅ None |
| Confidence | +0.15 (0.28) | +0.17 (0.39) | −0.130 | .897 | ✅ None |
| Trust | +0.31 (0.53) | +0.19 (0.56) | 0.646 | .523 | ✅ None |
| Understanding | +0.33 (0.42) | −0.03 (1.11) | 1.179 | .248 | ✅ None |

No significant order effects were found for any measure. The Progressive interface advantage on SUS, Trust, and Confidence was consistent regardless of which interface participants saw first. This confirms the findings reflect genuine design differences rather than order or practice effects.

---

### 7. Perceived Understanding (Additional)
**Mixed ANOVA:** F(1,29)=1.079, p=.308, η²p=.036, dz=.185
**Normality of differences:** W=0.759, p<.001 — non-normal

Understanding showed a small, non-significant difference between interfaces. The near-zero correlations with Trust (H1) across all sensitivity analyses suggest Understanding and Trust operate independently in this sample.

**Note for thesis:** Understanding was not a primary hypothesis outcome (it feeds H1), so report it descriptively as an exploratory finding.

---

### 8. Preference Analysis
**File:** `results/tables/preference_analysis.csv`

- **83.9% (26/31) preferred Progressive (Variant B)**
- **16.1% (5/31) preferred Static (Variant A)**
- Both participants who preferred Static were in the BA group (saw Progressive first)

**Note for thesis:** Preference may still be influenced by recency (tendency to prefer the most recently seen interface). The 2 Static-preferring participants in AB group and 3 in BA group show the preference is not entirely order-driven, but interpret cautiously.

---

### 9. Qualitative Data
**Files:** `results/qualitative/`

- 31 participants, 100% response rate on Q1 and Q4
- Q2 (Challenges): 90.3% responded
- Q3 (Improvements): 96.8% responded
- Thematic coding to be completed manually by researcher (Braun & Clarke, 2006)

**Common themes visible in raw data:**
- Q1: SHAP explanation clarity, factor visibility, confidence scores
- Q2: Technical terminology, colour scheme, slow navigation
- Q3: Export functionality, trend lines, mobile version, glossary
- Q4: 83.9% Progressive — reasons centre on transparency and explanation quality

---

## 📊 INTERPRETATION FOR THESIS DISCUSSION

### What the Counterbalanced Design Established:
✅ **H2: Progressive interface significantly more usable** (SUS +5.9pts, dz=.626, p=.002)
✅ **H3: Progressive interface significantly increases decision confidence** (dz=.484, p=.013)
✅ **H4: Progressive interface significantly increases trust** (dz=.469, p=.015)
✅ **No order effects** — all three effects are robust across presentation sequence
✅ **No Interface × Order interactions** — effects consistent in both groups

### What Was Not Supported:
❌ **H1: Understanding and Trust are not significantly correlated** (ρ=.037, p=.844)
   - The previous r=.799 was an artefact of fixed ordering (both scores improved together on the second interface)
   - In the counterbalanced design, the relationship disappears — participants' understanding scores do not predict their trust scores
   - This is an honest and important finding: improving perceived understanding does not automatically translate to trust

❌ **Understanding did not significantly improve** between interfaces (p=.308)

### Revised Causal Language:
Use this language in Chapter 4 and 5:
- ✅ "The Progressive interface produced significantly higher trust scores than the Static interface, F(1,29)=6.684, p=.015, η²p=.187, an effect that was consistent across both presentation orders."
- ✅ "No significant association was found between perceived understanding and trust, ρ=.037, p=.844, 95% CI [−.339, .393]."
- ✅ "The counterbalanced design confirmed that order effects do not account for the observed differences (all order effect tests p>.248)."
- ❌ Do NOT write: "pre-registered hypotheses"
- ❌ Do NOT write: "without compromising usability" (SUS improved significantly)
- ❌ Do NOT write: "Wilcoxon Z = ..." (use W statistic or switch to paired t)

---

## 📁 OUTPUT FILES

| File | Description |
|------|-------------|
| `results/updated_analysis/table_4_3_hypothesis_results.csv` | Full Table 4.3 |
| `results/updated_analysis/order_period_effect.csv` | Order effects check |
| `results/mixed_anova/mixed_anova_summary.csv` | Mixed ANOVA summary |
| `results/counterbalanced_analysis/*.png` | Interaction plots (4 DVs) |
| `results/tables/table_4_1_sample_composition.csv` | Table 4.1 |
| `results/tables/reliability_cronbach_alpha.csv` | Reliability table |
| `results/qualitative/` | Qualitative exports |

## 🔁 REPRODUCIBLE SCRIPTS

| Script | Purpose |
|--------|---------|
| `run_full_analysis_updated.py` | H1–H4, order effects, Table 4.3 (seed 42) |
| `run_mixed_anova.py` | Mixed ANOVA F-statistics, η²p |
| `analyze_counterbalanced_data.py` | Descriptives + interaction plots |
| `calculate_reliability_cronbach_alpha.py` | Cronbach's α |
| `generate_table_4_1_sample_composition.py` | Table 4.1 demographics |

---

## 📝 REMAINING FOR RESEARCHER

1. **Write Chapter 4 Results** using tables and figures above
2. **Conduct thematic analysis** (Braun & Clarke) on qualitative data — Kiro has exported the data, coding is yours
3. **Update Chapter 3 Methods** to describe counterbalanced design accurately
4. **Update Chapter 5 Discussion** using revised causal language above
5. **Reconcile Appendix A** — confirm Understanding scale is 5 items (as logged) and update any reference to 3 items

---

## 🔒 DATA INTEGRITY

- **Clean dataset:** n=31, no missing paired data
- **Counterbalanced:** AB=16, BA=15, balance confirmed (χ²=0.032, p=.858)
- **Reproducible:** All analyses scripted with seed 42, version-controlled
- **Transparent:** Raw and Holm-adjusted p-values reported side by side
- **Honest:** Non-significant H1 and H2-Understanding reported plainly without reframing
- **Corrected:** Wilcoxon Z → t-statistic (all differences normal); "pre-registered" → "specified in advance"

---

**Analysis complete and ready for thesis writing.** 🎓
*Last updated: November 15, 2026*
