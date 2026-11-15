"""
Table 4.1: Sample Composition (Demographics)
============================================
Generates demographic breakdown of final sample (n=31)
"""

import pandas as pd
from pathlib import Path

# Ensure output directory exists
Path("results/tables").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("TABLE 4.1: SAMPLE COMPOSITION")
print("=" * 80)

# Load data
df = pd.read_csv('data/clean/analysis_paired.csv')
n = len(df)

print(f"\nTotal sample: n = {n}")

# ============================================================================
# Demographics Breakdown
# ============================================================================

demographics = []

# Age Group
print("\n" + "-" * 80)
print("AGE GROUP")
print("-" * 80)
age_counts = df['age_group'].value_counts().sort_index()
for age, count in age_counts.items():
    pct = (count / n) * 100
    print(f"  {age}: {count} ({pct:.1f}%)")
    demographics.append({
        'Characteristic': 'Age Group',
        'Category': age,
        'n': count,
        'Percentage': f"{pct:.1f}%"
    })

# Gender
print("\n" + "-" * 80)
print("GENDER")
print("-" * 80)
gender_counts = df['gender'].value_counts().sort_index()
for gender, count in gender_counts.items():
    pct = (count / n) * 100
    print(f"  {gender}: {count} ({pct:.1f}%)")
    demographics.append({
        'Characteristic': 'Gender',
        'Category': gender,
        'n': count,
        'Percentage': f"{pct:.1f}%"
    })

# Education Level
print("\n" + "-" * 80)
print("EDUCATION LEVEL")
print("-" * 80)
edu_counts = df['education_level'].value_counts()
for edu, count in edu_counts.items():
    pct = (count / n) * 100
    print(f"  {edu}: {count} ({pct:.1f}%)")
    demographics.append({
        'Characteristic': 'Education Level',
        'Category': edu,
        'n': count,
        'Percentage': f"{pct:.1f}%"
    })

# Role
print("\n" + "-" * 80)
print("CURRENT ROLE")
print("-" * 80)
role_counts = df['role'].value_counts()
for role, count in role_counts.items():
    pct = (count / n) * 100
    print(f"  {role}: {count} ({pct:.1f}%)")
    demographics.append({
        'Characteristic': 'Current Role',
        'Category': role,
        'n': count,
        'Percentage': f"{pct:.1f}%"
    })

# Years of Experience
print("\n" + "-" * 80)
print("YEARS OF TEACHING EXPERIENCE")
print("-" * 80)
exp_order = ['0-2 years', '3-5 years', '6-10 years', '11-15 years', '16+ years']
exp_counts = df['years_experience'].value_counts()
for exp in exp_order:
    if exp in exp_counts.index:
        count = exp_counts[exp]
        pct = (count / n) * 100
        print(f"  {exp}: {count} ({pct:.1f}%)")
        demographics.append({
            'Characteristic': 'Years of Experience',
            'Category': exp,
            'n': count,
            'Percentage': f"{pct:.1f}%"
        })

# Familiarity with Analytics (binary: 1=No, 5=Yes)
print("\n" + "-" * 80)
print("FAMILIARITY WITH LEARNING ANALYTICS")
print("-" * 80)
fam_labels = {
    1: 'No (not familiar with decision tools)',
    5: 'Yes (familiar with decision tools)'
}
fam_counts = df['familiarity_with_analytics'].value_counts().sort_index()
for fam_num, count in fam_counts.items():
    fam_label = fam_labels.get(fam_num, str(fam_num))
    pct = (count / n) * 100
    print(f"  {fam_label}: {count} ({pct:.1f}%)")
    demographics.append({
        'Characteristic': 'Familiarity with Analytics',
        'Category': fam_label,
        'n': count,
        'Percentage': f"{pct:.1f}%"
    })

# ============================================================================
# Save Table 4.1
# ============================================================================

df_table41 = pd.DataFrame(demographics)
df_table41.to_csv('results/tables/table_4_1_sample_composition.csv', index=False)

print("\n" + "=" * 80)
print("✓ Saved: results/tables/table_4_1_sample_composition.csv")
print("=" * 80)
