"""
Hypothesis Testing - Chapter 4 Results
======================================
Follows analysis_spec_for_kiro.md requirements exactly.

Hypotheses:
H1: Understanding ↔ Trust (positive association)
H2: SUS (Progressive > Static)
H3: Decision Confidence (Progressive > Static)
H4: Trust (Progressive > Static)

Random seed: 42 for reproducibility
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import shapiro, ttest_rel, wilcoxon, pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Create output directories
Path("results/tables").mkdir(parents=True, exist_ok=True)
Path("results/figures").mkdir(parents=True, exist_ok=True)
Path("results/appendix").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("HYPOTHESIS TESTING - CHAPTER 4")
print("=" * 80)
print(f"\nRandom seed: 42")
print(f"Alpha: 0.05 (two-tailed)")
print(f"Multiplicity: Raw p-values (primary), Holm-adjusted (sensitivity)")

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n" + "=" * 80)
print("1. LOADING ANALYSIS DATA")
print("=" * 80)

df = pd.read_csv('data/clean/analysis_paired.csv')
n = len(df)

print(f"\nSample size: n = {n}")
print(f"All participants have complete paired data: {df['complete_paired'].all()}")

# ============================================================================
# 2. DESCRIPTIVE STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("2. DESCRIPTIVE STATISTICS")
print("=" * 80)

measures = {
    'SUS': ('sus_A', 'sus_B'),
    'Trust': ('trust_A', 'trust_B'),
    'Understanding': ('understanding_A', 'understanding_B'),
    'Decision Confidence': ('confidence_A', 'confidence_B')
}

descriptives = []

for measure_name, (var_a, var_b) in measures.items():
    # Static (Variant A)
    mean_a = df[var_a].mean()
    sd_a = df[var_a].std(ddof=1)
    median_a = df[var_a].median()
    q1_a = df[var_a].quantile(0.25)
    q3_a = df[var_a].quantile(0.75)
    
    # Progressive (Variant B)
    mean_b = df[var_b].mean()
    sd_b = df[var_b].std(ddof=1)
    median_b = df[var_b].median()
    q1_b = df[var_b].quantile(0.25)
    q3_b = df[var_b].quantile(0.75)
    
    descriptives.append({
        'Measure': measure_name,
        'Condition': 'Static (A)',
        'Mean': f"{mean_a:.2f}",
        'SD': f"{sd_a:.2f}",
        'Median': f"{median_a:.2f}",
        'IQR': f"{q1_a:.2f}–{q3_a:.2f}"
    })
    
    descriptives.append({
        'Measure': measure_name,
        'Condition': 'Progressive (B)',
        'Mean': f"{mean_b:.2f}",
        'SD': f"{sd_b:.2f}",
        'Median': f"{median_b:.2f}",
        'IQR': f"{q1_b:.2f}–{q3_b:.2f}"
    })
    
    print(f"\n{measure_name}:")
    print(f"  Static (A):      M = {mean_a:.2f}, SD = {sd_a:.2f}, Mdn = {median_a:.2f}")
    print(f"  Progressive (B): M = {mean_b:.2f}, SD = {sd_b:.2f}, Mdn = {median_b:.2f}")

# Save Table 4.2
df_descriptives = pd.DataFrame(descriptives)
df_descriptives.to_csv('results/tables/table_4_2_descriptives.csv', index=False)
print(f"\n✓ Saved: results/tables/table_4_2_descriptives.csv")

# ============================================================================
# 3. HELPER FUNCTIONS
# ============================================================================

def cohens_dz(diff):
    """Cohen's dz for paired samples (difference / SD of differences)."""
    return diff.mean() / diff.std(ddof=1)

def paired_rank_biserial(x, y):
    """Matched-pairs rank-biserial correlation for Wilcoxon test."""
    diff = y - x
    n_pos = (diff > 0).sum()
    n_neg = (diff < 0).sum()
    return (n_pos - n_neg) / (n_pos + n_neg)

def holm_correction(p_values):
    """Holm-Bonferroni correction for multiple comparisons."""
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    
    adjusted = np.zeros(n)
    for i, p in enumerate(sorted_p):
        adjusted[sorted_indices[i]] = min(p * (n - i), 1.0)
    
    return adjusted

def test_normality_and_compare(var_a, var_b, measure_name, hypothesis):
    """
    Test normality of paired differences, then run appropriate test.
    Returns dict with all test results.
    """
    diff = df[var_b] - df[var_a]
    
    # Normality test on differences
    shapiro_stat, shapiro_p = shapiro(diff)
    is_normal = shapiro_p > 0.05
    
    # Paired t-test (always calculate)
    t_stat, t_p = ttest_rel(df[var_a], df[var_b])
    t_df = n - 1
    
    # Calculate 95% CI for mean difference
    mean_diff = diff.mean()
    se_diff = diff.std(ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, t_df)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    
    # Cohen's dz
    dz = cohens_dz(diff)
    
    # Wilcoxon signed-rank test (always calculate)
    w_stat, w_p = wilcoxon(df[var_a], df[var_b], alternative='two-sided')
    
    # Rank-biserial correlation
    r_rb = paired_rank_biserial(df[var_a].values, df[var_b].values)
    
    # Determine primary test
    if is_normal:
        primary_test = "Paired t-test"
        primary_stat = t_stat
        primary_df = t_df
        primary_p = t_p
        primary_effect = dz
        primary_effect_name = "Cohen's dz"
        concordance_test = f"Wilcoxon Z (p = {w_p:.3f})"
    else:
        primary_test = "Wilcoxon signed-rank"
        primary_stat = w_stat
        primary_df = "—"
        primary_p = w_p
        primary_effect = r_rb
        primary_effect_name = "Rank-biserial r"
        concordance_test = f"Paired t (p = {t_p:.3f})"
    
    # Check direction
    direction_correct = mean_diff > 0  # Progressive (B) > Static (A)
    
    return {
        'hypothesis': hypothesis,
        'measure': measure_name,
        'n': n,
        'mean_a': df[var_a].mean(),
        'mean_b': df[var_b].mean(),
        'mean_diff': mean_diff,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'shapiro_w': shapiro_stat,
        'shapiro_p': shapiro_p,
        'is_normal': is_normal,
        'primary_test': primary_test,
        'primary_stat': primary_stat,
        'primary_df': primary_df,
        'primary_p': primary_p,
        'primary_effect': primary_effect,
        'primary_effect_name': primary_effect_name,
        'cohens_dz': dz,
        't_stat': t_stat,
        't_p': t_p,
        'w_stat': w_stat,
        'w_p': w_p,
        'rank_biserial': r_rb,
        'concordance': concordance_test,
        'direction_correct': direction_correct
    }

# ============================================================================
# 4. HYPOTHESIS 1: Understanding ↔ Trust (Correlation)
# ============================================================================

print("\n" + "=" * 80)
print("H1: UNDERSTANDING ↔ TRUST (POSITIVE ASSOCIATION)")
print("=" * 80)

# Primary analysis: participant-average across both conditions
understanding_avg = df['understanding_avg']
trust_avg = df['trust_avg']

# Test normality for correlation method choice
_, p_und = shapiro(understanding_avg)
_, p_trust = shapiro(trust_avg)
both_normal = (p_und > 0.05) and (p_trust > 0.05)

if both_normal:
    r, p_val = pearsonr(understanding_avg, trust_avg)
    corr_type = "Pearson"
    # Calculate 95% CI using Fisher z-transformation
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    z_crit = 1.96
    ci_lower = np.tanh(z - z_crit * se)
    ci_upper = np.tanh(z + z_crit * se)
else:
    r, p_val = spearmanr(understanding_avg, trust_avg)
    corr_type = "Spearman"
    # Bootstrap CI for Spearman (simplified)
    ci_lower, ci_upper = np.nan, np.nan  # Would need bootstrap

print(f"\nPrimary Analysis: Participant-average (n = {n})")
print(f"  Normality: Understanding p = {p_und:.3f}, Trust p = {p_trust:.3f}")
print(f"  Test: {corr_type} correlation")
print(f"  r = {r:.3f}, p = {p_val:.3f}")
if not np.isnan(ci_lower):
    print(f"  95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"  Result: {'Significant' if p_val < 0.05 else 'Not significant'} positive association")

h1_result = {
    'hypothesis': 'H1',
    'test': f'{corr_type} correlation',
    'r': r,
    'p': p_val,
    'ci_lower': ci_lower if not np.isnan(ci_lower) else '—',
    'ci_upper': ci_upper if not np.isnan(ci_upper) else '—',
    'n': n,
    'supported': (p_val < 0.05) and (r > 0)
}

# Sensitivity analyses
print(f"\nSensitivity Analyses:")

# Within each condition
for condition, var_u, var_t in [('Static', 'understanding_A', 'trust_A'), 
                                  ('Progressive', 'understanding_B', 'trust_B')]:
    r_cond, p_cond = pearsonr(df[var_u], df[var_t])
    print(f"  {condition}: r = {r_cond:.3f}, p = {p_cond:.3f}")

# ============================================================================
# 5. HYPOTHESES 2-4: Paired Comparisons
# ============================================================================

print("\n" + "=" * 80)
print("H2-H4: PAIRED COMPARISONS (PROGRESSIVE > STATIC)")
print("=" * 80)

results_h2_h4 = []

# H2: SUS
print("\n" + "-" * 80)
print("H2: System Usability (SUS)")
print("-" * 80)
h2 = test_normality_and_compare('sus_A', 'sus_B', 'SUS', 'H2')
results_h2_h4.append(h2)

print(f"Normality: Shapiro-Wilk W = {h2['shapiro_w']:.3f}, p = {h2['shapiro_p']:.3f}")
print(f"  → {'Normal' if h2['is_normal'] else 'Non-normal'} distribution")
print(f"\nPrimary Test: {h2['primary_test']}")
print(f"  Statistic = {h2['primary_stat']:.3f}, df = {h2['primary_df']}, p = {h2['primary_p']:.3f}")
print(f"  Mean difference (B - A) = {h2['mean_diff']:.2f}, 95% CI [{h2['ci_lower']:.2f}, {h2['ci_upper']:.2f}]")
print(f"  Effect size ({h2['primary_effect_name']}) = {h2['primary_effect']:.3f}")
print(f"  Concordance: {h2['concordance']}")

# H3: Decision Confidence
print("\n" + "-" * 80)
print("H3: Decision Confidence")
print("-" * 80)
h3 = test_normality_and_compare('confidence_A', 'confidence_B', 'Confidence', 'H3')
results_h2_h4.append(h3)

print(f"Normality: Shapiro-Wilk W = {h3['shapiro_w']:.3f}, p = {h3['shapiro_p']:.3f}")
print(f"  → {'Normal' if h3['is_normal'] else 'Non-normal'} distribution")
print(f"\nPrimary Test: {h3['primary_test']}")
print(f"  Statistic = {h3['primary_stat']:.3f}, df = {h3['primary_df']}, p = {h3['primary_p']:.3f}")
print(f"  Mean difference (B - A) = {h3['mean_diff']:.2f}, 95% CI [{h3['ci_lower']:.2f}, {h3['ci_upper']:.2f}]")
print(f"  Effect size ({h3['primary_effect_name']}) = {h3['primary_effect']:.3f}")
print(f"  Concordance: {h3['concordance']}")

# H4: Trust
print("\n" + "-" * 80)
print("H4: Trust in AI")
print("-" * 80)
h4 = test_normality_and_compare('trust_A', 'trust_B', 'Trust', 'H4')
results_h2_h4.append(h4)

print(f"Normality: Shapiro-Wilk W = {h4['shapiro_w']:.3f}, p = {h4['shapiro_p']:.3f}")
print(f"  → {'Normal' if h4['is_normal'] else 'Non-normal'} distribution")
print(f"\nPrimary Test: {h4['primary_test']}")
print(f"  Statistic = {h4['primary_stat']:.3f}, df = {h4['primary_df']}, p = {h4['primary_p']:.3f}")
print(f"  Mean difference (B - A) = {h4['mean_diff']:.2f}, 95% CI [{h4['ci_lower']:.2f}, {h4['ci_upper']:.2f}]")
print(f"  Effect size ({h4['primary_effect_name']}) = {h4['primary_effect']:.3f}")
print(f"  Concordance: {h4['concordance']}")

# ============================================================================
# 6. MULTIPLICITY CORRECTION (HOLM)
# ============================================================================

print("\n" + "=" * 80)
print("MULTIPLICITY CORRECTION (H2-H4)")
print("=" * 80)

raw_p_values = [h2['primary_p'], h3['primary_p'], h4['primary_p']]
holm_p_values = holm_correction(raw_p_values)

print(f"\n{'Hypothesis':<12} {'Raw p':<10} {'Holm p':<10} {'Decision (α=.05)'}")
print("-" * 50)
for i, (hyp, raw_p, holm_p) in enumerate(zip(['H2', 'H3', 'H4'], raw_p_values, holm_p_values)):
    raw_sig = "Significant" if raw_p < 0.05 else "Not significant"
    holm_sig = "Significant" if holm_p < 0.05 else "Not significant"
    print(f"{hyp:<12} {raw_p:<10.3f} {holm_p:<10.3f} Raw: {raw_sig}")
    print(f"{'':>35} Holm: {holm_sig}")

# ============================================================================
# 7. CREATE TABLE 4.3: HYPOTHESIS TEST RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("CREATING TABLE 4.3: HYPOTHESIS TEST RESULTS")
print("=" * 80)

table_rows = []

# H1
table_rows.append({
    'Hypothesis': 'H1',
    'Test': h1_result['test'],
    'Statistic': f"r = {h1_result['r']:.3f}",
    'df': '—',
    'p (raw)': f"{h1_result['p']:.3f}",
    'p (Holm)': '—',
    'Effect Size': f"r = {h1_result['r']:.3f}",
    '95% CI': f"[{h1_result['ci_lower']}, {h1_result['ci_upper']}]" if h1_result['ci_lower'] != '—' else '—',
    'Direction': 'Positive' if h1_result['r'] > 0 else 'Negative',
    'Supported': 'Yes' if h1_result['supported'] else 'No'
})

# H2-H4
for i, result in enumerate([h2, h3, h4]):
    table_rows.append({
        'Hypothesis': result['hypothesis'],
        'Test': result['primary_test'],
        'Statistic': f"{result['primary_stat']:.3f}",
        'df': result['primary_df'],
        'p (raw)': f"{result['primary_p']:.3f}",
        'p (Holm)': f"{holm_p_values[i]:.3f}",
        'Effect Size': f"{result['primary_effect_name']}: {result['primary_effect']:.3f}",
        '95% CI': f"[{result['ci_lower']:.2f}, {result['ci_upper']:.2f}]",
        'Direction': 'B > A' if result['direction_correct'] else 'A > B',
        'Supported': 'Yes' if (result['primary_p'] < 0.05 and result['direction_correct']) else 'No'
    })

df_table43 = pd.DataFrame(table_rows)
df_table43.to_csv('results/tables/table_4_3_hypothesis_tests.csv', index=False)
print(f"✓ Saved: results/tables/table_4_3_hypothesis_tests.csv")

print("\n" + "=" * 80)
print("HYPOTHESIS TESTING COMPLETE")
print("=" * 80)
print(f"\nResults saved to: results/tables/")
print(f"  - table_4_2_descriptives.csv")
print(f"  - table_4_3_hypothesis_tests.csv")
print("\n" + "=" * 80)
