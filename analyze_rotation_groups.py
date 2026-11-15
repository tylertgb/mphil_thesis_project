"""
Rotation Group Analysis
=======================
Check if task case allocation (rotation groups) affected results.
Per Study_Task_Case_Allocation: 3 rotation groups, 6 cases per participant.

This is an EXPLORATORY analysis (not pre-registered).
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# Create output directory
Path("results/exploratory").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ROTATION GROUP ANALYSIS (EXPLORATORY)")
print("=" * 80)

# Load data
df = pd.read_csv('data/clean/analysis_paired.csv')
n = len(df)

print(f"\nTotal sample: n = {n}")

# ============================================================================
# Check if rotation_group exists
# ============================================================================

if 'rotation_group' not in df.columns:
    print("\n" + "=" * 80)
    print("NOTE: rotation_group column not found in analysis_paired.csv")
    print("=" * 80)
    print("""
This analysis requires a 'rotation_group' column (1, 2, or 3) indicating
which case allocation each participant received.

If rotation groups were used in the study, the column needs to be added
to the demographics or analysis_paired.csv file.

For now, this analysis cannot be completed.
""")
    
    # Save a note
    with open('results/exploratory/rotation_group_analysis_NOTE.txt', 'w') as f:
        f.write("""Rotation Group Analysis - NOT COMPLETED

The study design mentioned rotation groups (Study_Task_Case_Allocation.docx),
but the rotation_group identifier is not present in the current dataset.

To complete this analysis:
1. Identify which rotation group each participant was assigned to
2. Add a 'rotation_group' column (1, 2, or 3) to the data
3. Re-run this script

This is an exploratory analysis and was not pre-registered, so it is
not required for the main hypothesis tests.
""")
    
    print("✓ Saved note: results/exploratory/rotation_group_analysis_NOTE.txt")
    print("=" * 80)
    
else:
    # ============================================================================
    # Analyze rotation groups
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("ROTATION GROUP DISTRIBUTION")
    print("=" * 80)
    
    rotation_counts = df['rotation_group'].value_counts().sort_index()
    
    print("\nParticipants per rotation group:")
    for group, count in rotation_counts.items():
        pct = (count / n) * 100
        print(f"  Group {group}: {count} ({pct:.1f}%)")
    
    # ============================================================================
    # Compare difference scores across rotation groups
    # ============================================================================
    
    print("\n" + "=" * 80)
    print("ROTATION GROUP EFFECTS ON DIFFERENCE SCORES")
    print("=" * 80)
    
    measures = {
        'SUS': ('sus_A', 'sus_B'),
        'Trust': ('trust_A', 'trust_B'),
        'Understanding': ('understanding_A', 'understanding_B'),
        'Confidence': ('confidence_A', 'confidence_B')
    }
    
    results = []
    
    for measure_name, (var_a, var_b) in measures.items():
        df[f'{measure_name}_diff'] = df[var_b] - df[var_a]
        
        print(f"\n{measure_name} (Progressive - Static):")
        print("-" * 60)
        
        # Descriptives per group
        for group in sorted(df['rotation_group'].unique()):
            group_data = df[df['rotation_group'] == group][f'{measure_name}_diff']
            print(f"  Group {group}: M = {group_data.mean():+.3f}, SD = {group_data.std():.3f}, n = {len(group_data)}")
        
        # Kruskal-Wallis test (non-parametric ANOVA)
        groups_data = [df[df['rotation_group'] == g][f'{measure_name}_diff'].values 
                       for g in sorted(df['rotation_group'].unique())]
        
        if len(groups_data) >= 2:
            h_stat, p_val = stats.kruskal(*groups_data)
            
            print(f"\n  Kruskal-Wallis H = {h_stat:.3f}, p = {p_val:.3f}")
            
            if p_val < 0.05:
                print(f"  ⚠️ Significant difference across rotation groups (p < .05)")
                interpretation = "Significant difference"
            else:
                print(f"  ✓ No significant difference across rotation groups")
                interpretation = "No significant difference"
            
            results.append({
                'Measure': measure_name,
                'H-statistic': f"{h_stat:.3f}",
                'p-value': f"{p_val:.3f}",
                'Interpretation': interpretation
            })
    
    # ============================================================================
    # Save results
    # ============================================================================
    
    df_results = pd.DataFrame(results)
    df_results.to_csv('results/exploratory/rotation_group_analysis.csv', index=False)
    
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    print("""
This is an EXPLORATORY analysis (not pre-registered).

If rotation groups show significant effects, it suggests that:
- Different task cases may have varying difficulty
- Case allocation affected participant responses

For the thesis:
- Report this as exploratory
- Note that rotation was intended to balance task effects
- If significant, discuss as a limitation or interesting finding
- Do not use to adjust the main hypothesis tests
""")
    
    print("\n✓ Saved: results/exploratory/rotation_group_analysis.csv")
    print("=" * 80)
