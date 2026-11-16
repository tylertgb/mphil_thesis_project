"""
Verify AB/BA assignments for ALL 31 participants from timestamps.
─────────────────────────────────────────────────────────────────
For BA participants, variant_b (Progressive) should be logged
BEFORE variant_a (Static) — because they did Progressive first.
If variant_a is logged first for a BA participant, that is a mismatch.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("study_data")
trust = pd.read_csv(DATA_DIR / "trust_responses.csv")
dem   = pd.read_csv(DATA_DIR / "demographics.csv")

# Get first timestamp per participant per condition from trust
ts = trust[['participant_id','condition','timestamp']].copy()
ts['timestamp'] = pd.to_datetime(ts['timestamp'])

# For each participant, find which condition was logged first
first_ts = ts.sort_values('timestamp').groupby('participant_id').first().reset_index()
first_ts = first_ts.rename(columns={'condition': 'first_logged_condition'})

# Merge with assigned order
check = dem[['participant_id','presentation_order']].merge(
        first_ts[['participant_id','first_logged_condition']], on='participant_id')

# Derive expected first condition from assignment
# AB = Static first → variant_a logged first
# BA = Progressive first → variant_b logged first
check['expected_first'] = check['presentation_order'].map({
    'AB': 'variant_a',
    'BA': 'variant_b'
})
check['match'] = check['first_logged_condition'] == check['expected_first']

# Full table
print("ALL 31 PARTICIPANTS — Assignment vs Timestamp")
print("=" * 75)
print(f"{'Participant ID':<30} {'Assigned':>8} {'Expected 1st':>14} {'Actual 1st':>12} {'Match':>7}")
print("-" * 75)
for _, row in check.iterrows():
    icon = '✅' if row['match'] else '❌'
    print(f"{row['participant_id']:<30} {row['presentation_order']:>8} "
          f"{row['expected_first']:>14} {row['first_logged_condition']:>12} {icon:>7}")

n_match    = check['match'].sum()
n_mismatch = (~check['match']).sum()
print(f"\nMatched: {n_match}/31  |  Mismatched: {n_mismatch}/31")

if n_mismatch > 0:
    print("\nMISMATCHED PARTICIPANTS:")
    mismatches = check[~check['match']]
    for _, row in mismatches.iterrows():
        print(f"  {row['participant_id']}: assigned {row['presentation_order']} "
              f"but {row['first_logged_condition']} was logged first")

# ── Key question: are ALL BA participants logging variant_a first? ─
print("\n\nBA participants — which condition was logged first?")
ba = check[check['presentation_order'] == 'BA']
print(ba[['participant_id','first_logged_condition','match']].to_string(index=False))

print("\n\nAB participants — which condition was logged first?")
ab = check[check['presentation_order'] == 'AB']
print(ab[['participant_id','first_logged_condition','match']].to_string(index=False))

# ── Actual timestamps side by side for all BA participants ─────────
print("\n\nBA participants — actual timestamps (variant_a vs variant_b):")
print(f"{'Participant ID':<30} {'variant_a timestamp':>35} {'variant_b timestamp':>35} {'a_before_b':>12}")
print("-" * 115)

ba_ids = ba['participant_id'].tolist()
for pid in ba_ids:
    t_a = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_a')]['timestamp'].values
    t_b = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_b')]['timestamp'].values
    if len(t_a) and len(t_b):
        a_before_b = t_a[0] < t_b[0]
        print(f"{pid:<30} {t_a[0]:>35} {t_b[0]:>35} {str(a_before_b):>12}")
