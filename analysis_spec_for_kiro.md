# Analysis Spec for Kiro: Chapter 4 (Results)

**Purpose:** Make the analysis match the study as proposed and as described in Chapter 3, so Chapter 4 reports what the study set out to test, nothing more and nothing quietly different.

**Sources of truth (do not contradict these):**
- Hypotheses H1–H4 (proposal §1.5)
- Chapter 3 §3.7 (measures) and §3.8 (analysis plan)
- `questionnaire_exact_wording.md` (items as administered)
- `Study_Task_Case_Allocation.docx` (rotation groups, 6 cases per participant)
- `run_hypothesis_tests.py` (starting point; update as described below)

**Core rule:** Everything in Section 2 is pre-declared. Do not change tests, alpha, tails, or exclusion rules after looking at results. Anything added later must be labelled **exploratory**.

---

## 1. Data readiness (before any statistics)

1. Freeze the dataset: take a full export of the raw data and a backup copy, mark the raw file read-only, and record its file hash. All cleaning must happen in a script, never by hand-editing the raw file.
2. Reconcile the count: the final sample should be 30 complete participants. Remove pilot and developer test sessions by a documented rule (for example, IDs used before the first real participant), and report how the number reconciles.
3. Completeness: every included participant must have both conditions (Static and Progressive) and all questionnaire sections. No imputation. Exclude only for technical failure or incompleteness, never because of outcomes.
4. Balance report: participants per rotation group (1/2/3) and per interface order (Static-first vs Progressive-first).
5. Logged integrity: duplicate participant IDs, impossible values (outside 1–5), and a quick screen for straight-lining or implausibly short sessions. Report these; do not exclude post hoc. If you think someone should be excluded, report results with and without them.

---

## 2. Scoring and pre-declared tests

**Scoring must follow the items actually administered.** Two items need confirming before scoring (see Section 7).

| Measure | Score | Note |
|---|---|---|
| SUS | Odd items (r − 1), even items (5 − r), sum × 2.5 → 0–100 | Standard Brooke (1996) scoring |
| Trust | Mean of items (1–5) | Custom 5-item scale, none reverse-coded |
| Perceived Understanding | Mean of items (1–5) | **Confirm 3 vs 5 items** |
| Decision Confidence | Mean of items (1–5) | **Confirm item structure** |

**Unit of analysis:** one score per participant per condition (wide format: `sus_A`, `sus_B`, and so on).

| Hypothesis | Variable | Test | Direction |
|---|---|---|---|
| H1 | Understanding ↔ Trust | Pearson or Spearman (by normality) | Positive association |
| H2 | SUS | Paired comparison, Progressive vs Static | Progressive higher |
| H3 | Decision Confidence | Paired comparison | Progressive higher |
| H4 | Trust | Paired comparison | Progressive higher |

**Rules for H2–H4:**
- Paired t-test, or Wilcoxon signed-rank if Shapiro–Wilk on the paired differences indicates non-normality (Chapter 3 states this rule). Also report the other test as a concordance check.
- **Two-tailed, α = .05**, as in the power analysis. Do not switch to one-tailed. A hypothesis counts as supported only if the result is significant **and** the mean difference is in the predicted direction.
- Report for each: mean and SD per condition, mean difference with 95% CI, test statistic, df, p, and effect size (Cohen's dz for the t-test; matched-pairs rank-biserial correlation for Wilcoxon).
- **Multiplicity:** report raw p and Holm-adjusted p for H2–H4 side by side. The researcher states in advance which one is the decision rule (Section 7).

**Rules for H1:**
- **Primary:** correlation between each participant's average Understanding and average Trust across both conditions (n = 30, one point per person). This avoids treating two scores from the same person as independent.
- **Sensitivity:** pooled scores (n = 60, label the non-independence) and a repeated-measures correlation (for example `pingouin.rm_corr`), plus the correlation within each condition separately.
- Report r or rho with a 95% CI (Fisher z for Pearson; bootstrap with seed 42 for Spearman).

---

## 3. Checks to run alongside the hypothesis tests

- **Order/period effect:** compare each participant's difference score (Progressive − Static) between the Static-first and Progressive-first groups. A systematic difference indicates an order effect. Group sizes are small, so treat this as descriptive and report it honestly.
- **Rotation group effect:** compare difference scores across the 3 rotation groups (exploratory).
- **Reliability:** Cronbach's alpha for SUS, Trust, Understanding, and Decision Confidence, per condition. Trust, Understanding, and Confidence are not validated instruments, so report alpha and note that n = 30 gives rough estimates.
- **Sample composition:** counts by role/group (UDS staff, BACE staff, postgraduate students) and AI experience from Section A. Descriptive only. With groups this small, make no inferential subgroup claims.
- **Optional sensitivity:** if per-case ratings exist, a mixed model with random intercepts for participant and case.
- **Distribution checks:** Q–Q plots and histograms of the paired differences, saved to an appendix folder.

---

## 4. Qualitative data (Section F)

- Export the four open-ended responses with participant IDs, once per participant (no condition field).
- Thematic analysis follows Braun & Clarke (2006): familiarization, coding, themes, review, definition, write-up. **The researcher does the coding and theme decisions.** Kiro may organize and export the data, but must not present machine-generated themes as findings. If any AI assistance is used, it must be disclosed and every theme checked against the raw quotes.
- Q4 (preferred interface): report counts and percentages for Static vs Progressive, then the coded reasons. Check whether stated preference agrees with each participant's own score differences, and report where it does not.

---

## 5. Outputs Kiro should produce (reproducible, seed 42, pinned versions)

- `data/clean/analysis_wide.csv` and a **cleaning log** listing every exclusion and the rule applied
- Table 4.1: sample composition
- Table 4.2: descriptives per condition (mean, SD, median, IQR)
- Table 4.3: H1–H4 results (test used, statistic, df, raw p, Holm p, effect size, 95% CI, direction, supported yes/no)
- Table 4.4: reliability
- Figure: paired plot per measure (each participant's Static vs Progressive score, with condition means)
- Figure: scatter of participant-average Understanding vs Trust, with fit line (H1)
- One script that reproduces every number from the frozen raw export, plus a README of run order

---

## 6. Reporting and interpretation rules

- A non-significant result means no evidence of a difference **at this sample size**, not evidence of no difference. Always show the effect size and CI. The design can reliably detect only dz ≥ 0.53 at n = 30.
- Do not add or drop participants to chase significance. Stop at the planned 30.
- If the observed results disagree with a hypothesis, report that plainly. Do not reframe the hypothesis.
- Any departure from Chapter 3 §3.8 (for example, a different test after a normality failure) is documented in Chapter 4 as a deviation with the reason.
- Describe the sample as a convenience sample; do not generalize beyond it.

---

## 7. Open items the researcher must settle first

1. **Perceived Understanding: 3 or 5 items?** Appendix A and the proposal list 5; an earlier note from the implementation said 3. Check what the app actually presented. Score what was administered, and make Appendix A, Chapter 3, and Chapter 4 describe the same instrument.
2. **Decision Confidence structure:** Appendix A lists 4 items per condition, but an earlier note mentioned per-task confidence ratings. Confirm what was collected and how it is aggregated to one score per condition.
3. **Multiplicity decision rule for H2–H4:** raw p, or Holm-adjusted p. Decide before running.
4. **Exclusion criteria:** write them down now, before the data is analysed.
5. **Proposal §3.7** lists SUS and Trust but omits Decision Confidence (H3). Update it so the analysis plan covers all four hypotheses.
