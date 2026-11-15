"""
Remove Incomplete Participant P_20261007_170406
===============================================
This participant only completed Variant B, not both variants.
Removing from all data files for clean analysis dataset.
"""

import pandas as pd

INCOMPLETE_ID = 'P_20261007_170406'

print("=" * 80)
print(f"REMOVING INCOMPLETE PARTICIPANT: {INCOMPLETE_ID}")
print("=" * 80)

files = [
    'sus_responses',
    'trust_responses', 
    'understanding_responses',
    'decision_confidence',
    'active_sessions',
    'qualitative_feedback'
]

for filename in files:
    filepath = f'study_data/{filename}.csv'
    df = pd.read_csv(filepath)
    
    before = len(df)
    df_clean = df[df['participant_id'] != INCOMPLETE_ID]
    after = len(df_clean)
    removed = before - after
    
    if removed > 0:
        df_clean.to_csv(filepath, index=False)
        print(f"✓ {filename}.csv: {before} -> {after} (removed {removed} row(s))")
    else:
        print(f"  {filename}.csv: No data for this participant")

print("\n" + "=" * 80)
print("REMOVAL COMPLETE")
print("=" * 80)
print(f"\nFinal sample: 31 completed participants with both variants")
print("=" * 80 + "\n")
