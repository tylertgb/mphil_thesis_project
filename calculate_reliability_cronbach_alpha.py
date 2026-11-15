"""
Reliability Analysis - Cronbach's Alpha
======================================
Calculate internal consistency for all multi-item scales:
- SUS (10 items)
- Trust (5 items)
- Understanding (5 items)
- Decision Confidence (4 items per task, aggregated per condition)
"""

import pandas as pd
import numpy as np
from pathlib import Path

def cronbach_alpha(data):
    """
    Calculate Cronbach's alpha for internal consistency.
    
    Parameters:
    -----------
    data : DataFrame or array-like
        Each column is an item, each row is a respondent
        
    Returns:
    --------
    alpha : float
        Cronbach's alpha coefficient
    """
    data = pd.DataFrame(data)
    n_items = data.shape[1]
    
    if n_items < 2:
        return np.nan
    
    # Variance of each item
    item_variances = data.var(axis=0, ddof=1)
    
    # Variance of total scores
    total_scores = data.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    
    # Cronbach's alpha formula
    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    
    return alpha

# Create output directories
Path("results/tables").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("RELIABILITY ANALYSIS - CRONBACH'S ALPHA")
print("=" * 80)

# ============================================================================
# Load raw item-level data
# ============================================================================

print("\nLoading item-level data...")

sus_raw = pd.read_csv('study_data/sus_responses.csv')
trust_raw = pd.read_csv('study_data/trust_responses.csv')
understanding_raw = pd.read_csv('study_data/understanding_responses.csv')
confidence_raw = pd.read_csv('study_data/decision_confidence.csv')

reliability_results = []

# ============================================================================
# 1. SUS (10 items)
# ============================================================================

print("\n" + "=" * 80)
print("1. SYSTEM USABILITY SCALE (SUS)")
print("=" * 80)

sus_items = [f'item_{i}' for i in range(1, 11)]

# SUS reverse-coding: items 2, 4, 6, 8, 10 need to be reversed (6 - item)
def reverse_code_sus(df_sus):
    """Reverse code SUS items 2, 4, 6, 8, 10 for reliability analysis."""
    df_coded = df_sus.copy()
    reverse_items = ['item_2', 'item_4', 'item_6', 'item_8', 'item_10']
    for item in reverse_items:
        df_coded[item] = 6 - df_coded[item]
    return df_coded

# Variant A (Static)
sus_a_raw = sus_raw[sus_raw['condition'] == 'variant_a'][sus_items]
sus_a = reverse_code_sus(sus_a_raw)
alpha_sus_a = cronbach_alpha(sus_a)
print(f"\nVariant A (Static):")
print(f"  n = {len(sus_a)}, items = 10")
print(f"  Cronbach's α = {alpha_sus_a:.3f}")

# Variant B (Progressive)
sus_b_raw = sus_raw[sus_raw['condition'] == 'variant_b'][sus_items]
sus_b = reverse_code_sus(sus_b_raw)
alpha_sus_b = cronbach_alpha(sus_b)
print(f"\nVariant B (Progressive):")
print(f"  n = {len(sus_b)}, items = 10")
print(f"  Cronbach's α = {alpha_sus_b:.3f}")

# Overall (both conditions)
sus_all_raw = sus_raw[sus_items]
sus_all = reverse_code_sus(sus_all_raw)
alpha_sus_all = cronbach_alpha(sus_all)
print(f"\nOverall (both conditions):")
print(f"  n = {len(sus_all)}, items = 10")
print(f"  Cronbach's α = {alpha_sus_all:.3f}")

reliability_results.extend([
    {
        'Scale': 'SUS',
        'Condition': 'Static (A)',
        'n': len(sus_a),
        'Items': 10,
        'Cronbach α': f"{alpha_sus_a:.3f}",
        'Interpretation': 'Excellent' if alpha_sus_a >= 0.9 else 'Good' if alpha_sus_a >= 0.8 else 'Acceptable' if alpha_sus_a >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'SUS',
        'Condition': 'Progressive (B)',
        'n': len(sus_b),
        'Items': 10,
        'Cronbach α': f"{alpha_sus_b:.3f}",
        'Interpretation': 'Excellent' if alpha_sus_b >= 0.9 else 'Good' if alpha_sus_b >= 0.8 else 'Acceptable' if alpha_sus_b >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'SUS',
        'Condition': 'Overall',
        'n': len(sus_all),
        'Items': 10,
        'Cronbach α': f"{alpha_sus_all:.3f}",
        'Interpretation': 'Excellent' if alpha_sus_all >= 0.9 else 'Good' if alpha_sus_all >= 0.8 else 'Acceptable' if alpha_sus_all >= 0.7 else 'Questionable'
    }
])

# ============================================================================
# 2. Trust (5 items)
# ============================================================================

print("\n" + "=" * 80)
print("2. TRUST IN AI SCALE")
print("=" * 80)

trust_items = [f'trust_{i}' for i in range(1, 6)]

# Variant A (Static)
trust_a = trust_raw[trust_raw['condition'] == 'variant_a'][trust_items]
alpha_trust_a = cronbach_alpha(trust_a)
print(f"\nVariant A (Static):")
print(f"  n = {len(trust_a)}, items = 5")
print(f"  Cronbach's α = {alpha_trust_a:.3f}")

# Variant B (Progressive)
trust_b = trust_raw[trust_raw['condition'] == 'variant_b'][trust_items]
alpha_trust_b = cronbach_alpha(trust_b)
print(f"\nVariant B (Progressive):")
print(f"  n = {len(trust_b)}, items = 5")
print(f"  Cronbach's α = {alpha_trust_b:.3f}")

# Overall
trust_all = trust_raw[trust_items]
alpha_trust_all = cronbach_alpha(trust_all)
print(f"\nOverall (both conditions):")
print(f"  n = {len(trust_all)}, items = 5")
print(f"  Cronbach's α = {alpha_trust_all:.3f}")

reliability_results.extend([
    {
        'Scale': 'Trust',
        'Condition': 'Static (A)',
        'n': len(trust_a),
        'Items': 5,
        'Cronbach α': f"{alpha_trust_a:.3f}",
        'Interpretation': 'Excellent' if alpha_trust_a >= 0.9 else 'Good' if alpha_trust_a >= 0.8 else 'Acceptable' if alpha_trust_a >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Trust',
        'Condition': 'Progressive (B)',
        'n': len(trust_b),
        'Items': 5,
        'Cronbach α': f"{alpha_trust_b:.3f}",
        'Interpretation': 'Excellent' if alpha_trust_b >= 0.9 else 'Good' if alpha_trust_b >= 0.8 else 'Acceptable' if alpha_trust_b >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Trust',
        'Condition': 'Overall',
        'n': len(trust_all),
        'Items': 5,
        'Cronbach α': f"{alpha_trust_all:.3f}",
        'Interpretation': 'Excellent' if alpha_trust_all >= 0.9 else 'Good' if alpha_trust_all >= 0.8 else 'Acceptable' if alpha_trust_all >= 0.7 else 'Questionable'
    }
])

# ============================================================================
# 3. Understanding (5 items)
# ============================================================================

print("\n" + "=" * 80)
print("3. UNDERSTANDING SCALE")
print("=" * 80)

understanding_items = [f'understanding_{i}' for i in range(1, 6)]

# Variant A (Static)
und_a = understanding_raw[understanding_raw['condition'] == 'variant_a'][understanding_items]
alpha_und_a = cronbach_alpha(und_a)
print(f"\nVariant A (Static):")
print(f"  n = {len(und_a)}, items = 5")
print(f"  Cronbach's α = {alpha_und_a:.3f}")

# Variant B (Progressive)
und_b = understanding_raw[understanding_raw['condition'] == 'variant_b'][understanding_items]
alpha_und_b = cronbach_alpha(und_b)
print(f"\nVariant B (Progressive):")
print(f"  n = {len(und_b)}, items = 5")
print(f"  Cronbach's α = {alpha_und_b:.3f}")

# Overall
und_all = understanding_raw[understanding_items]
alpha_und_all = cronbach_alpha(und_all)
print(f"\nOverall (both conditions):")
print(f"  n = {len(und_all)}, items = 5")
print(f"  Cronbach's α = {alpha_und_all:.3f}")

reliability_results.extend([
    {
        'Scale': 'Understanding',
        'Condition': 'Static (A)',
        'n': len(und_a),
        'Items': 5,
        'Cronbach α': f"{alpha_und_a:.3f}",
        'Interpretation': 'Excellent' if alpha_und_a >= 0.9 else 'Good' if alpha_und_a >= 0.8 else 'Acceptable' if alpha_und_a >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Understanding',
        'Condition': 'Progressive (B)',
        'n': len(und_b),
        'Items': 5,
        'Cronbach α': f"{alpha_und_b:.3f}",
        'Interpretation': 'Excellent' if alpha_und_b >= 0.9 else 'Good' if alpha_und_b >= 0.8 else 'Acceptable' if alpha_und_b >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Understanding',
        'Condition': 'Overall',
        'n': len(und_all),
        'Items': 5,
        'Cronbach α': f"{alpha_und_all:.3f}",
        'Interpretation': 'Excellent' if alpha_und_all >= 0.9 else 'Good' if alpha_und_all >= 0.8 else 'Acceptable' if alpha_und_all >= 0.7 else 'Questionable'
    }
])

# ============================================================================
# 4. Decision Confidence (4 items per task)
# ============================================================================

print("\n" + "=" * 80)
print("4. DECISION CONFIDENCE SCALE")
print("=" * 80)

confidence_items = [f'confidence_{i}' for i in range(1, 5)]

# Variant A (Static) - aggregate across all tasks
conf_a = confidence_raw[confidence_raw['condition'] == 'variant_a'][confidence_items]
alpha_conf_a = cronbach_alpha(conf_a)
print(f"\nVariant A (Static):")
print(f"  n = {len(conf_a)} task responses, items = 4")
print(f"  Cronbach's α = {alpha_conf_a:.3f}")

# Variant B (Progressive)
conf_b = confidence_raw[confidence_raw['condition'] == 'variant_b'][confidence_items]
alpha_conf_b = cronbach_alpha(conf_b)
print(f"\nVariant B (Progressive):")
print(f"  n = {len(conf_b)} task responses, items = 4")
print(f"  Cronbach's α = {alpha_conf_b:.3f}")

# Overall
conf_all = confidence_raw[confidence_items]
alpha_conf_all = cronbach_alpha(conf_all)
print(f"\nOverall (both conditions):")
print(f"  n = {len(conf_all)} task responses, items = 4")
print(f"  Cronbach's α = {alpha_conf_all:.3f}")

reliability_results.extend([
    {
        'Scale': 'Decision Confidence',
        'Condition': 'Static (A)',
        'n': len(conf_a),
        'Items': 4,
        'Cronbach α': f"{alpha_conf_a:.3f}",
        'Interpretation': 'Excellent' if alpha_conf_a >= 0.9 else 'Good' if alpha_conf_a >= 0.8 else 'Acceptable' if alpha_conf_a >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Decision Confidence',
        'Condition': 'Progressive (B)',
        'n': len(conf_b),
        'Items': 4,
        'Cronbach α': f"{alpha_conf_b:.3f}",
        'Interpretation': 'Excellent' if alpha_conf_b >= 0.9 else 'Good' if alpha_conf_b >= 0.8 else 'Acceptable' if alpha_conf_b >= 0.7 else 'Questionable'
    },
    {
        'Scale': 'Decision Confidence',
        'Condition': 'Overall',
        'n': len(conf_all),
        'Items': 4,
        'Cronbach α': f"{alpha_conf_all:.3f}",
        'Interpretation': 'Excellent' if alpha_conf_all >= 0.9 else 'Good' if alpha_conf_all >= 0.8 else 'Acceptable' if alpha_conf_all >= 0.7 else 'Questionable'
    }
])

# ============================================================================
# Save Results
# ============================================================================

df_reliability = pd.DataFrame(reliability_results)
df_reliability.to_csv('results/tables/reliability_cronbach_alpha.csv', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nInterpretation guidelines (George & Mallery, 2003):")
print("  α ≥ 0.9 : Excellent")
print("  α ≥ 0.8 : Good")
print("  α ≥ 0.7 : Acceptable")
print("  α ≥ 0.6 : Questionable")
print("  α < 0.6 : Poor")

print("\n✓ Saved: results/tables/reliability_cronbach_alpha.csv")
print("=" * 80)
