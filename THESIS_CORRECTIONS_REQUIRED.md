# THESIS CORRECTIONS REQUIRED
**Critical Issues to Address Before Defense**

---

## 🔴 CRITICAL ISSUE #1: Fixed Order Design

### **CONFIRMED:**
- **ALL 31 participants** saw Static (Variant A) FIRST, then Progressive (Variant B)
- Order and treatment are **completely confounded**
- Verified via: `verify_order.py` (all 31 show variant_a → variant_b)

### **Required Changes:**

#### **Chapter 3 (Methodology) - MUST REWORD:**
❌ **REMOVE:** Any mention of "counterbalanced order"

✅ **ADD:** Clear description of fixed order:
```
"Participants experienced both interface conditions in a fixed order: 
all participants first used the Static interface (Variant A), followed 
by the Progressive Disclosure interface (Variant B). This within-subjects 
design with fixed order was chosen to ensure consistency across participants 
but introduces a confound between presentation order and interface design."
```

✅ **ADD to Limitations (Section 3.9 or 3.10):**
```
"Order Effects: The fixed presentation order (Static first, Progressive second) 
means that observed differences cannot be attributed solely to interface design. 
Improvements in trust and confidence under Progressive may reflect practice 
effects, increased familiarity with the task, or the interface design itself. 
A counterbalanced design would be needed to isolate these effects."
```

#### **Chapter 4 (Results) - MUST CHANGE LANGUAGE:**

❌ **REMOVE causal language:**
- "Progressive significantly increases trust"
- "Progressive significantly increases confidence"
- "Progressive interface enhances..."

✅ **REPLACE with descriptive language:**
- "Trust scores were significantly higher under Progressive (Variant B) in this fixed-order design"
- "Participants reported higher confidence when using Progressive (the second interface)"
- "Under Progressive (presented second), trust scores were..."

✅ **ADD caveat to each significant result:**
```
"Note: Because all participants experienced Static first and Progressive 
second, this difference may reflect order effects (practice, familiarity) 
rather than, or in addition to, the interface design itself."
```

#### **Chapter 5 (Discussion) - MUST ADDRESS:**

✅ **Major Limitation Section:**
```
The most significant limitation of this study is the fixed presentation order. 
All participants experienced the Static interface first, then the Progressive 
interface. This design decision, while ensuring consistency, confounds order 
effects with treatment effects. The observed improvements in trust (p = .001) 
and decision confidence (p = .004) under Progressive may be attributable to:

1. Practice effects: Participants became more comfortable with the task
2. Learning effects: Familiarity with the prediction context increased
3. Interface design: Progressive disclosure genuinely improved experience
4. Recency bias: The 83.9% preference for Progressive may reflect recent exposure

The non-significant difference in usability (SUS, p = .192) does NOT rule 
out order effects, as different measures respond differently to practice and 
familiarity. A counterbalanced design (half seeing Progressive first) would 
be necessary to isolate the interface effect from order effects.

Future research should employ counterbalancing or collect a reversed-order 
cohort to estimate the magnitude of order effects and establish the true 
interface effect.
```

✅ **Interpretation of Preference (83.9% for Progressive):**
```
The strong preference for Progressive (83.9%) should be interpreted cautiously 
given the fixed order. Recency effects (favoring the last-seen option) and 
learning effects may inflate this preference beyond what would be observed 
in a counterbalanced design.
```

---

## 🟡 CRITICAL ISSUE #2: Statistical Reporting Errors

### **Fix #1: Wilcoxon Statistic Name**

❌ **INCORRECT:** "Wilcoxon Z = 100.5" / "Wilcoxon Z = 55.0"

✅ **CORRECT:** "Wilcoxon W = 100.5" or "Wilcoxon signed-rank statistic = 100.5"

**Where to fix:**
- Table 4.3: Change column header from "Z" to "W"
- Results text: Use "W statistic" not "Z statistic"
- Already correct in `run_hypothesis_tests.py` output ("Statistic = ")

### **Fix #2: "Pre-registered" Language**

❌ **INCORRECT:** "pre-registered analysis"

✅ **CORRECT:** "analysis specified in advance" or "planned analysis"

**Rationale:** No formal pre-registration (e.g., OSF, AsPredicted)

**Where to fix:**
- Anywhere claiming "pre-registered"
- Use: "Following the analysis plan specified in Chapter 3..."

### **Fix #3: Usability Claims**

❌ **INCORRECT:** "Progressive disclosure maintains usability" or "without compromising usability"

✅ **CORRECT:** "No evidence of a usability difference between conditions"

**Full recommended statement:**
```
"There was no statistically significant difference in usability (SUS) 
between conditions (t(30) = -1.334, p = .192, 95% CI [-1.7, 8.2]). 
This non-significant result indicates insufficient evidence to conclude 
that Progressive differs from Static in usability, though the confidence 
interval includes both small negative and moderate positive differences."
```

**Rationale:** 
- p > .05 is NOT evidence of equivalence
- 95% CI: [-1.7, 8.2] SUS points is wide, includes meaningful differences
- Cannot claim "no difference," only "no evidence of difference at n=31"

### **Fix #4: H1 Causation**

❌ **INCORRECT:** "Understanding causes trust" or "Understanding leads to trust"

✅ **CORRECT:** "Understanding and trust are strongly positively associated"

**Where to fix:**
- Any causal language about H1
- It's correlation in self-report data, not causation
- Both could be caused by third variable (e.g., general engagement)

---

## 🟡 ISSUE #3: Document Reconciliation

### **Fix #1: Appendix A Demographics (Section A)**

**Problem:** Appendix A doesn't match actual demographics collected

✅ **UPDATE Appendix A Section A to include:**
```
Demographics Collected:
1. Age group (18-29, 30-39, 40-49, 50-59, 60+)
2. Gender (Male, Female, Other, Prefer not to say)
3. Education level (Bachelor's, Master's, Doctoral)
4. Current role (Lecturer, Assistant Lecturer, Tutor, Student, etc.)
5. Years of teaching experience (0-2, 3-5, 6-10, 11-15, 16+)
6. AI experience (None, Basic, Moderate, Advanced)
7. Familiarity with learning analytics decision tools (Yes/No)
```

### **Fix #2: Participant Selection Criteria**

**Problem:** 48.4% reported NO analytics familiarity, contradicts "familiar with data-driven decision-making" criterion

✅ **REWORD criteria in Chapter 3:**

❌ **REMOVE:** "Participants must be familiar with data-driven decision-making"

✅ **REPLACE with:**
```
"Participants were educational stakeholders (lecturers, tutors, administrators, 
or postgraduate students) involved in or learning about educational contexts. 
No prior experience with learning analytics or AI systems was required, 
allowing evaluation across diverse familiarity levels (48.4% reported no prior 
familiarity with analytics decision tools, 51.6% reported prior familiarity)."
```

### **Fix #3: Table 4.1 - Add Role/Institution Breakdown**

**Currently missing:** Breakdown by institution/group

✅ **ADD to Table 4.1 or separate table:**
```
Sample Composition by Affiliation:
- UDS Academic Staff: X (X%)
- BACE Staff: X (X%)
- Postgraduate Students: X (X%)
- Other: X (X%)
```

**Action needed:** Check recruitment sources and code participants by affiliation if possible

### **Fix #4: Understanding Scale Items (STILL UNCONFIRMED)**

**Problem:** Spec says "confirm 3 vs 5 items"

✅ **VERIFICATION NEEDED:**
- Check `questionnaire_exact_wording.md` or actual interface code
- Reliability analysis shows 5 items: understanding_1 to understanding_5
- **CONFIRM:** All 5 items were actually presented to participants
- **UPDATE:** Appendix A to list all 5 items with exact wording

**Current status:** Assumed 5 items based on data, but need to verify against actual questionnaire

### **Fix #5: Decision Confidence Structure (STILL UNCONFIRMED)**

**Problem:** Spec says "confirm item structure"

✅ **VERIFICATION NEEDED:**
- Data shows 4 items: confidence_1 to confidence_4
- Were these administered **per task** (3 tasks × 4 items = 12 per condition)?
- Or **per condition** (4 items once per condition)?
- **Current analysis:** Treats as per-condition aggregate

**Action:** Verify with interface code or questionnaire documentation

---

## 🟢 ISSUE #4: Sample Size Reporting

### **Current: n = 31 (target was 30)**

✅ **CORRECT WAY TO REPORT:**
```
"Data collection targeted 30 participants based on the a priori power 
analysis. Collection yielded 37 participants, of which 6 were excluded 
for abandoning the study before completion, and 1 was excluded for 
completing only one condition. The final sample comprised 31 participants 
with complete paired data across both conditions. No analyses were conducted 
until data collection closed."
```

✅ **Confirm in thesis:**
- No interim analyses were run
- Exclusions were rule-based (incomplete data), not outcome-based
- Final n=31 provides 82% power for dz=0.53 (close to planned 80% for dz=0.53 at n=30)

---

## 🟢 ISSUE #5: What's Actually Solid

### **These are CORRECT and well-done:**

✅ **Reliability Analysis**
- Cronbach's α for all scales
- Good to excellent internal consistency
- Proper reporting with interpretation

✅ **Reproducible Scripts**
- All analyses scripted with seed 42
- Version-controlled
- Outputs traceable

✅ **Raw p-values + Holm Adjustment**
- Transparent multiplicity handling
- Both reported side-by-side
- Conservative approach

✅ **H1 (Understanding ↔ Trust)**
- Strongest result (r = .799, p < .001)
- Robust across sensitivity analyses
- Proper interpretation as association, not causation (after fixing)

✅ **Qualitative Data Export**
- Well-structured for manual coding
- Instructions provided
- Response rates documented

---

## 📋 ACTION CHECKLIST

### **High Priority (Before Defense):**

- [ ] **Verify order statement in Chapter 3** - Remove "counterbalanced," add fixed-order description
- [ ] **Rewrite Results language** - Remove causal claims, add order caveats
- [ ] **Add major limitation section** - Address order confound explicitly
- [ ] **Fix Table 4.3** - Change "Z" to "W" for Wilcoxon
- [ ] **Fix "pre-registered" language** - Use "specified in advance"
- [ ] **Fix usability claims** - Change to "no evidence of difference"
- [ ] **Update Appendix A Section A** - Match actual demographics collected
- [ ] **Reword participant criteria** - Remove "familiar with analytics" requirement

### **Medium Priority:**

- [ ] **Add Table 4.1 affiliation breakdown** - If data available
- [ ] **Verify Understanding scale** - Confirm all 5 items were used
- [ ] **Verify Confidence structure** - Per-task or per-condition?
- [ ] **Update preference interpretation** - Note recency bias

### **Before Submitting:**

- [ ] **Read through Chapter 3** - Ensure no "counterbalanced" remains
- [ ] **Read through Chapter 4** - Ensure no causal language remains
- [ ] **Check Chapter 5** - Major limitation section present
- [ ] **Verify all tables** - Statistics correctly labeled
- [ ] **Check figure captions** - Note fixed-order design where relevant

---

## 💬 WHAT TO SAY IF ASKED ABOUT ORDER

### **If Defense is Tomorrow:**

> "Data collection is complete with 31 participants. Analysis is underway. 
> The study used a within-subjects design with fixed presentation order—all 
> participants experienced the Static interface first, followed by Progressive. 
> This introduces a confound between order and treatment that will be 
> addressed as a major limitation in the final thesis."

### **If Examiner Asks "Why Fixed Order?"**

> "The fixed order was a design decision made during implementation to ensure 
> consistency across participants and simplify the deployment logistics. In 
> retrospect, counterbalancing would have strengthened causal inference. 
> The limitation is acknowledged, and results are interpreted accordingly 
> as associations in a fixed-order design rather than causal effects."

---

## 📊 REVISED HYPOTHESIS CONCLUSIONS

### **H1: Understanding ↔ Trust**
✅ **SUPPORTED** - Strong positive association (r = .799, p < .001)
- Most defensible result
- Robust across conditions
- Association, not causation

### **H2: SUS (Usability)**
❌ **NOT SUPPORTED** - No evidence of difference (p = .192)
- Cannot claim equivalence
- Wide CI [-1.7, 8.2]
- Insufficient power to detect small differences

### **H3: Decision Confidence**
⚠️ **SUPPORTED WITH CAVEAT** - Higher under Progressive (p = .004)
- **CONFOUNDED with order**
- May reflect practice effects
- Interpret as: "Confidence was higher when using the second interface (Progressive)"

### **H4: Trust in AI**
⚠️ **SUPPORTED WITH CAVEAT** - Higher under Progressive (p = .001)
- **CONFOUNDED with order**
- May reflect familiarity effects
- Interpret as: "Trust was higher when using the second interface (Progressive)"

---

## 🎯 FINAL MESSAGE

**The analysis is technically sound and thorough.** The main issue is the **fixed-order design**, which is a **methodological limitation**, not an analysis error.

**Key points:**
1. **Acknowledge the limitation clearly and early**
2. **Reframe results as descriptive, not causal**
3. **Don't oversell the preference data**
4. **H1 (correlation) remains strong**
5. **Your scripted, reproducible analysis is a strength**

**You have a solid thesis with one major limitation that needs honest reporting.**

---

**Generated:** 2026-11-15  
**Verified via:** `verify_order.py`  
**All 31 participants confirmed:** variant_a → variant_b
