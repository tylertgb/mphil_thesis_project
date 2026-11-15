"""
Order/Period Effects Analysis
=============================
Check if presentation order (which variant participants saw first) affected results.
Note: All participants saw Static (A) first, then Progressive (B) by design.
This checks for practice/fatigue effects.
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# Create output directories
Path("results/tables").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ORDER/PERIOD EFFECTS ANALYSIS")
print("=" * 80)

# Load data
df = pd.read_csv('data/clean/analysis_paired.csv')
n = len(df)

print(f"\nSample: n = {n}")
print("\nStudy Design: All participants experienced conditions in the same order:")
print("  1. Variant A (Static) FIRST")
print("  2. Variant B (Progressive) SECOND")

# ============================================================================
# Practice/Fatigue Effects
# ============================================================================

print("\n" + "=" * 80)
print("CHECKING FOR PRACTICE/FATIGUE EFFECTS")
print("=" * 80)

print("\nSince all participants saw conditions in the same order (A→B),")
print("we cannot separate order effects from treatment effects.")
print("\nHowever, we can check if the pattern of results suggests:")
print("  - Practice effects: Performance improves over time (B > A)")
print("  - Fatigue effects: Performance declines over time (B < A)")

# Calculate differences
measures = {
    'SUS': ('sus_A', 'sus_B'),
    'Trust': ('trust_A', 'trust_B'),
    'Understanding': ('understanding_A', 'understanding_B'),
    'Confidence': ('confidence_A', 'confidence_B')
}

print("\n" + "-" * 80)
print("Direction of Effects (Progressive - Static)")
print("-" * 80)

results = []

for measure_name, (var_a, var_b) in measures.items():
    diff = df[var_b] - df[var_a]
    mean_diff = diff.mean()
    
    n_improved = (diff > 0).sum()
    n_declined = (diff < 0).sum()
    n_unchanged = (diff == 0).sum()
    
    pct_improved = (n_improved / n) * 100
    pct_declined = (n_declined / n) * 100
    
    # Determine predominant pattern
    if n_improved > n_declined:
        pattern = "Improvement (suggests practice effect OR treatment effect)"
    elif n_declined > n_improved:
        pattern = "Decline (suggests fatigue effect OR negative treatment effect)"
    else:
        pattern = "Mixed/No clear pattern"
    
    print(f"\n{measure_name}:")
    print(f"  Mean difference: {mean_diff:+.3f}")
    print(f"  Improved (B > A): {n_improved} ({pct_improved:.1f}%)")
    print(f"  Declined (B < A): {n_declined} ({pct_declined:.1f}%)")
    print(f"  Unchanged: {n_unchanged}")
    print(f"  Pattern: {pattern}")
    
    results.append({
        'Measure': measure_name,
        'Mean Difference (B-A)': f"{mean_diff:+.3f}",
        'n Improved': n_improved,
        '% Improved': f"{pct_improved:.1f}%",
        'n Declined': n_declined,
        '% Declined': f"{pct_declined:.1f}%",
        'Predominant Pattern': pattern
    })

# ============================================================================
# Save Results
# ============================================================================

df_order = pd.DataFrame(results)
df_order.to_csv('results/tables/order_effects_check.csv', index=False)

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

print("""
IMPORTANT NOTES:

1. **Design Limitation**: This study used a fixed order design where all 
   participants experienced Static (A) first, then Progressive (B). This means
   we CANNOT separate:
   - True treatment effects (Progressive vs Static)
   - Order effects (first vs second presentation)
   - Time effects (practice, fatigue, learning)

2. **What We Observe**:
   - If B > A consistently: Could be treatment effect OR practice effect
   - If B < A consistently: Could be treatment effect OR fatigue effect
   - If mixed results: Suggests order effects may be minimal

3. **Mitigating Factors**:
   - Both interfaces used identical tasks and data
   - Session duration was reasonable (~25-30 minutes)
   - Participants were motivated educators (not fatigued undergrads)
   - Instructions emphasized equal attention to both interfaces

4. **For Thesis Discussion**:
   - Acknowledge this as a limitation
   - Note that a counterbalanced design would be needed to isolate effects
   - Argue that the pattern of results (some measures improve, some don't)
     suggests order effects alone cannot explain all findings
""")

print("\n✓ Saved: results/tables/order_effects_check.csv")
print("=" * 80)
