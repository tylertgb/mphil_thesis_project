"""
Data Preparation for Analysis - Chapter 4
==========================================
Converts raw study data to wide format for hypothesis testing.
Follows analysis_spec_for_kiro.md requirements.

Output: clean/analysis_wide.csv with one row per participant
"""

import pandas as pd
import numpy as np
import hashlib
from pathlib import Path

# Create output directory
Path("data/clean").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("DATA PREPARATION FOR ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. DATA LOADING & INTEGRITY CHECK
# ============================================================================

print("\n1. LOADING RAW DATA")

demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')

print(f"   Demographics: {len(demographics)} entries")
print(f"   Qualitative: {len(qualitative)} participants")
print(f"   SUS: {len(sus)} responses")
print(f"   Trust: {len(trust)} responses")
print(f"   Understanding: {len(understanding)} responses")
print(f"   Decision confidence: {len(decision_confidence)} records")

# Get completed participant IDs
completed_ids = set(qualitative['participant_id'])
print(f"\n   Completed participants: {len(completed_ids)}")

# ============================================================================
# 2. SCORING FUNCTIONS
# ============================================================================

def calculate_sus_score(responses):
    """
    Calculate SUS score following Brooke (1996).
    Odd items: (response - 1)
    Even items: (5 - response)
    Sum × 2.5 → 0-100 scale
    """
    score = 0
    for i, r in enumerate(responses, 1):
        if i % 2 == 1:  # Odd items
            score += (r - 1)
        else:  # Even items
            score += (5 - r)
    return score * 2.5

def calculate_mean_score(responses):
    """Calculate mean for Trust, Understanding, Decision Confidence."""
    return np.mean(responses)

# ============================================================================
# 3. PREPARE WIDE FORMAT DATA
# ============================================================================

print("\n2. CONVERTING TO WIDE FORMAT")

analysis_data = []

for pid in sorted(completed_ids):
    # Check if participant has demographics
    demo_match = demographics[demographics['participant_id'] == pid]
    if len(demo_match) == 0:
        print(f"   Warning: {pid} in qualitative but not in demographics - skipping")
        continue
    
    row = {'participant_id': pid}
    
    # Demographics
    demo = demo_match.iloc[0]
    row['age_group'] = demo['age_group']
    row['gender'] = demo['gender']
    row['education_level'] = demo['education_level']
    row['role'] = demo['role']
    row['years_experience'] = demo['years_experience']
    row['familiarity_with_analytics'] = demo['familiarity_with_analytics']
    
    # SUS - Variant A and B
    sus_a = sus[(sus['participant_id'] == pid) & (sus['condition'] == 'variant_a')]
    sus_b = sus[(sus['participant_id'] == pid) & (sus['condition'] == 'variant_b')]
    
    if len(sus_a) > 0:
        row['sus_A'] = sus_a['sus_score'].values[0]
    else:
        row['sus_A'] = np.nan
    
    if len(sus_b) > 0:
        row['sus_B'] = sus_b['sus_score'].values[0]
    else:
        row['sus_B'] = np.nan
    
    # Trust - Variant A and B (use pre-calculated means)
    trust_a = trust[(trust['participant_id'] == pid) & (trust['condition'] == 'variant_a')]
    trust_b = trust[(trust['participant_id'] == pid) & (trust['condition'] == 'variant_b')]
    
    if len(trust_a) > 0:
        row['trust_A'] = trust_a['trust_mean'].values[0]
    else:
        row['trust_A'] = np.nan
    
    if len(trust_b) > 0:
        row['trust_B'] = trust_b['trust_mean'].values[0]
    else:
        row['trust_B'] = np.nan
    
    # Understanding - Variant A and B (use pre-calculated means)
    und_a = understanding[(understanding['participant_id'] == pid) & (understanding['condition'] == 'variant_a')]
    und_b = understanding[(understanding['participant_id'] == pid) & (understanding['condition'] == 'variant_b')]
    
    if len(und_a) > 0:
        row['understanding_A'] = und_a['understanding_mean'].values[0]
    else:
        row['understanding_A'] = np.nan
    
    if len(und_b) > 0:
        row['understanding_B'] = und_b['understanding_mean'].values[0]
    else:
        row['understanding_B'] = np.nan
    
    # Decision Confidence - aggregate per condition (use pre-calculated means)
    # Each participant has 6 tasks total (3 per variant)
    conf_data = decision_confidence[decision_confidence['participant_id'] == pid]
    
    if len(conf_data) > 0:
        # Check if condition field exists
        if 'condition' in conf_data.columns:
            conf_a = conf_data[conf_data['condition'] == 'variant_a']
            conf_b = conf_data[conf_data['condition'] == 'variant_b']
        else:
            # Fallback: use temporal order (first half = variant_a, second half = variant_b)
            conf_sorted = conf_data.sort_values('timestamp')
            mid = len(conf_sorted) // 2
            conf_a = conf_sorted.iloc[:mid]
            conf_b = conf_sorted.iloc[mid:]
        
        # Calculate mean of confidence_mean across tasks per condition
        if len(conf_a) > 0:
            row['confidence_A'] = conf_a['confidence_mean'].mean()
        else:
            row['confidence_A'] = np.nan
        
        if len(conf_b) > 0:
            row['confidence_B'] = conf_b['confidence_mean'].mean()
        else:
            row['confidence_B'] = np.nan
    else:
        row['confidence_A'] = np.nan
        row['confidence_B'] = np.nan
    
    # Qualitative preference
    qual = qualitative[qualitative['participant_id'] == pid].iloc[0]
    row['preference'] = qual['q4_preference']
    
    # Calculate participant averages for H1
    if not np.isnan(row['understanding_A']) and not np.isnan(row['understanding_B']):
        row['understanding_avg'] = (row['understanding_A'] + row['understanding_B']) / 2
    else:
        row['understanding_avg'] = np.nan
    
    if not np.isnan(row['trust_A']) and not np.isnan(row['trust_B']):
        row['trust_avg'] = (row['trust_A'] + row['trust_B']) / 2
    else:
        row['trust_avg'] = np.nan
    
    analysis_data.append(row)

df_wide = pd.DataFrame(analysis_data)

print(f"   Created wide-format dataset: {len(df_wide)} participants")

# ============================================================================
# 4. EXCLUSION CRITERIA & COMPLETENESS CHECK
# ============================================================================

print("\n3. CHECKING DATA COMPLETENESS")

# Identify participants with complete paired data
df_wide['complete_paired'] = (
    ~df_wide['sus_A'].isna() & 
    ~df_wide['sus_B'].isna() &
    ~df_wide['trust_A'].isna() &
    ~df_wide['trust_B'].isna() &
    ~df_wide['understanding_A'].isna() &
    ~df_wide['understanding_B'].isna()
)

complete_count = df_wide['complete_paired'].sum()
incomplete_count = (~df_wide['complete_paired']).sum()

print(f"   Complete paired data: {complete_count} participants")
print(f"   Incomplete data: {incomplete_count} participants")

if incomplete_count > 0:
    print("\n   Participants with incomplete data:")
    incomplete = df_wide[~df_wide['complete_paired']]
    for _, row in incomplete.iterrows():
        missing = []
        if pd.isna(row['sus_A']): missing.append('SUS_A')
        if pd.isna(row['sus_B']): missing.append('SUS_B')
        if pd.isna(row['trust_A']): missing.append('Trust_A')
        if pd.isna(row['trust_B']): missing.append('Trust_B')
        if pd.isna(row['understanding_A']): missing.append('Understanding_A')
        if pd.isna(row['understanding_B']): missing.append('Understanding_B')
        print(f"      {row['participant_id']}: Missing {', '.join(missing)}")

# ============================================================================
# 5. SAVE OUTPUT
# ============================================================================

print("\n4. SAVING OUTPUT FILES")

# Save full dataset
df_wide.to_csv('data/clean/analysis_wide.csv', index=False)
print(f"   ✓ Saved: data/clean/analysis_wide.csv")

# Save paired-complete subset for hypothesis testing
df_paired = df_wide[df_wide['complete_paired']].copy()
df_paired.to_csv('data/clean/analysis_paired.csv', index=False)
print(f"   ✓ Saved: data/clean/analysis_paired.csv (n={len(df_paired)})")

# Create cleaning log
with open('data/clean/cleaning_log.txt', 'w') as f:
    f.write("DATA CLEANING LOG\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Date: 2026-11-14\n")
    f.write(f"Dataset frozen at commit: c49f33e\n\n")
    f.write(f"EXCLUSIONS:\n")
    f.write(f"1. Removed 6 abandoned participants (started but didn't complete)\n")
    f.write(f"   - P_20261107_230052\n")
    f.write(f"   - P_20261107_232520\n")
    f.write(f"   - P_20261111_064211\n")
    f.write(f"   - P_20261111_171940\n")
    f.write(f"   - P_20261111_172427\n")
    f.write(f"   - P_20261111_201640\n\n")
    f.write(f"2. Participants with incomplete paired data:\n")
    if incomplete_count > 0:
        for _, row in incomplete.iterrows():
            f.write(f"   - {row['participant_id']} (excluded from paired analyses)\n")
    else:
        f.write(f"   - None\n")
    f.write(f"\nFINAL SAMPLE:\n")
    f.write(f"   Total completed: {len(df_wide)} participants\n")
    f.write(f"   Complete paired data: {len(df_paired)} participants\n\n")
    f.write(f"ANALYSIS DECISIONS:\n")
    f.write(f"   - Multiplicity correction: Raw p-values primary, Holm as sensitivity\n")
    f.write(f"   - Normality test: Shapiro-Wilk on paired differences\n")
    f.write(f"   - If normal: Paired t-test; If non-normal: Wilcoxon signed-rank\n")
    f.write(f"   - Alpha = 0.05, two-tailed\n")

print(f"   ✓ Saved: data/clean/cleaning_log.txt")

print("\n" + "=" * 80)
print("DATA PREPARATION COMPLETE")
print("=" * 80)
print(f"\nReady for hypothesis testing with n={len(df_paired)} (paired analyses)")
print(f"Full sample n={len(df_wide)} (descriptives and Variant B standalone)")
print("\n" + "=" * 80)
