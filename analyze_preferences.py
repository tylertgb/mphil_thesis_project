"""
Preference Analysis
==================
Analyze which interface participants preferred and why.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Create output directories
Path("results/tables").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("PREFERENCE ANALYSIS")
print("=" * 80)

# Load data
df = pd.read_csv('data/clean/analysis_paired.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')

n = len(df)

# ============================================================================
# Overall Preference
# ============================================================================

print("\n" + "=" * 80)
print("OVERALL INTERFACE PREFERENCE")
print("=" * 80)

pref_counts = df['preference'].value_counts()

print(f"\nTotal participants: n = {n}")
print("\nPreference Distribution:")
for pref, count in pref_counts.items():
    pct = (count / n) * 100
    print(f"  {pref}: {count} ({pct:.1f}%)")

# ============================================================================
# Preference by Performance
# ============================================================================

print("\n" + "=" * 80)
print("PREFERENCE BY PERFORMANCE METRICS")
print("=" * 80)

# Group by preference
for pref in df['preference'].unique():
    pref_group = df[df['preference'] == pref]
    n_group = len(pref_group)
    
    print(f"\n{pref} (n = {n_group}):")
    print(f"  Mean SUS:")
    print(f"    Static (A): {pref_group['sus_A'].mean():.2f}")
    print(f"    Progressive (B): {pref_group['sus_B'].mean():.2f}")
    print(f"  Mean Trust:")
    print(f"    Static (A): {pref_group['trust_A'].mean():.2f}")
    print(f"    Progressive (B): {pref_group['trust_B'].mean():.2f}")
    print(f"  Mean Understanding:")
    print(f"    Static (A): {pref_group['understanding_A'].mean():.2f}")
    print(f"    Progressive (B): {pref_group['understanding_B'].mean():.2f}")
    print(f"  Mean Confidence:")
    print(f"    Static (A): {pref_group['confidence_A'].mean():.2f}")
    print(f"    Progressive (B): {pref_group['confidence_B'].mean():.2f}")

# ============================================================================
# Check Preference-Performance Alignment
# ============================================================================

print("\n" + "=" * 80)
print("PREFERENCE-PERFORMANCE ALIGNMENT")
print("=" * 80)

# Check if participants who preferred Progressive actually scored it higher
if 'Progressive' in pref_counts.index:
    pref_b = df[df['preference'] == 'Progressive']
    
    # Check if their trust was higher for B
    trust_aligned = (pref_b['trust_B'] > pref_b['trust_A']).sum()
    sus_aligned = (pref_b['sus_B'] > pref_b['sus_A']).sum()
    und_aligned = (pref_b['understanding_B'] > pref_b['understanding_A']).sum()
    conf_aligned = (pref_b['confidence_B'] > pref_b['confidence_A']).sum()
    
    n_pref_b = len(pref_b)
    
    print(f"\nParticipants who preferred Progressive (n = {n_pref_b}):")
    print(f"  Actually had higher Trust in Progressive: {trust_aligned} ({(trust_aligned/n_pref_b)*100:.1f}%)")
    print(f"  Actually had higher SUS in Progressive: {sus_aligned} ({(sus_aligned/n_pref_b)*100:.1f}%)")
    print(f"  Actually had higher Understanding in Progressive: {und_aligned} ({(und_aligned/n_pref_b)*100:.1f}%)")
    print(f"  Actually had higher Confidence in Progressive: {conf_aligned} ({(conf_aligned/n_pref_b)*100:.1f}%)")

if 'Static' in pref_counts.index:
    pref_a = df[df['preference'] == 'Static']
    
    trust_aligned = (pref_a['trust_A'] > pref_a['trust_B']).sum()
    sus_aligned = (pref_a['sus_A'] > pref_a['sus_B']).sum()
    und_aligned = (pref_a['understanding_A'] > pref_a['understanding_B']).sum()
    conf_aligned = (pref_a['confidence_A'] > pref_a['confidence_B']).sum()
    
    n_pref_a = len(pref_a)
    
    print(f"\nParticipants who preferred Static (n = {n_pref_a}):")
    print(f"  Actually had higher Trust in Static: {trust_aligned} ({(trust_aligned/n_pref_a)*100:.1f}%)")
    print(f"  Actually had higher SUS in Static: {sus_aligned} ({(sus_aligned/n_pref_a)*100:.1f}%)")
    print(f"  Actually had higher Understanding in Static: {und_aligned} ({(und_aligned/n_pref_a)*100:.1f}%)")
    print(f"  Actually had higher Confidence in Static: {conf_aligned} ({(conf_aligned/n_pref_a)*100:.1f}%)")

# ============================================================================
# Save Summary Table
# ============================================================================

preference_summary = []

for pref in df['preference'].unique():
    pref_group = df[df['preference'] == pref]
    n_group = len(pref_group)
    pct_group = (n_group / n) * 100
    
    preference_summary.append({
        'Preference': pref,
        'n': n_group,
        'Percentage': f"{pct_group:.1f}%",
        'Mean SUS (A)': f"{pref_group['sus_A'].mean():.2f}",
        'Mean SUS (B)': f"{pref_group['sus_B'].mean():.2f}",
        'Mean Trust (A)': f"{pref_group['trust_A'].mean():.2f}",
        'Mean Trust (B)': f"{pref_group['trust_B'].mean():.2f}",
        'Mean Understanding (A)': f"{pref_group['understanding_A'].mean():.2f}",
        'Mean Understanding (B)': f"{pref_group['understanding_B'].mean():.2f}",
        'Mean Confidence (A)': f"{pref_group['confidence_A'].mean():.2f}",
        'Mean Confidence (B)': f"{pref_group['confidence_B'].mean():.2f}"
    })

df_pref = pd.DataFrame(preference_summary)
df_pref.to_csv('results/tables/preference_analysis.csv', index=False)

print("\n✓ Saved: results/tables/preference_analysis.csv")
print("=" * 80)
