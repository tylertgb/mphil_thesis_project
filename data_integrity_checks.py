"""
Data Integrity Checks
====================
Pre-analysis checks for data quality:
1. Duplicate participant IDs
2. Values outside valid ranges (1-5 for Likert, 1-5 for SUS raw items)
3. Straight-lining detection
4. Implausibly short/long sessions
5. Missing data patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Create output directory
Path("results/data_quality").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("DATA INTEGRITY CHECKS")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
confidence = pd.read_csv('study_data/decision_confidence.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')

issues = []

# ============================================================================
# 1. DUPLICATE PARTICIPANT IDs
# ============================================================================

print("\n" + "=" * 80)
print("1. CHECKING FOR DUPLICATE PARTICIPANT IDs")
print("=" * 80)

all_ids = {
    'demographics': set(demographics['participant_id']),
    'sus': set(sus['participant_id']),
    'trust': set(trust['participant_id']),
    'understanding': set(understanding['participant_id']),
    'confidence': set(confidence['participant_id']),
    'qualitative': set(qualitative['participant_id'])
}

for name, ids in all_ids.items():
    duplicates = demographics[demographics['participant_id'].isin(ids)]['participant_id'].value_counts()
    duplicates = duplicates[duplicates > 1]
    
    if len(duplicates) > 0:
        print(f"\n❌ DUPLICATES in {name}:")
        for pid, count in duplicates.items():
            print(f"   {pid}: appears {count} times")
            issues.append({
                'Check': 'Duplicate IDs',
                'File': name,
                'Issue': f'{pid} appears {count} times',
                'Severity': 'HIGH'
            })
    else:
        print(f"\n✓ No duplicates in {name}")

# Check consistency across files
print("\n" + "-" * 80)
print("Checking ID consistency across files:")
print("-" * 80)

demo_ids = set(demographics['participant_id'])
for name, ids in all_ids.items():
    if name == 'demographics':
        continue
    
    missing_in_demo = ids - demo_ids
    missing_in_file = demo_ids - ids
    
    if missing_in_demo:
        print(f"\n⚠️ {name} has IDs not in demographics: {missing_in_demo}")
        issues.append({
            'Check': 'ID consistency',
            'File': name,
            'Issue': f'IDs in {name} but not demographics: {missing_in_demo}',
            'Severity': 'MEDIUM'
        })
    
    if missing_in_file:
        print(f"\n⚠️ Demographics has IDs not in {name}: {missing_in_file}")
        issues.append({
            'Check': 'ID consistency',
            'File': name,
            'Issue': f'IDs in demographics but not {name}: {missing_in_file}',
            'Severity': 'MEDIUM'
        })

if not issues:
    print("\n✓ All participant IDs are consistent across files")

# ============================================================================
# 2. VALUES OUTSIDE VALID RANGES
# ============================================================================

print("\n" + "=" * 80)
print("2. CHECKING FOR VALUES OUTSIDE VALID RANGES")
print("=" * 80)

# SUS items should be 1-5
sus_items = [f'item_{i}' for i in range(1, 11)]
sus_invalid = sus[sus_items].apply(lambda x: ((x < 1) | (x > 5)).sum())
if sus_invalid.sum() > 0:
    print(f"\n❌ SUS has {sus_invalid.sum()} values outside 1-5:")
    for item, count in sus_invalid[sus_invalid > 0].items():
        print(f"   {item}: {count} invalid values")
        issues.append({
            'Check': 'Valid range',
            'File': 'sus_responses',
            'Issue': f'{item} has {count} values outside 1-5',
            'Severity': 'HIGH'
        })
else:
    print("\n✓ All SUS items within valid range (1-5)")

# Trust items should be 1-5
trust_items = [f'trust_{i}' for i in range(1, 6)]
trust_invalid = trust[trust_items].apply(lambda x: ((x < 1) | (x > 5)).sum())
if trust_invalid.sum() > 0:
    print(f"\n❌ Trust has {trust_invalid.sum()} values outside 1-5:")
    for item, count in trust_invalid[trust_invalid > 0].items():
        print(f"   {item}: {count} invalid values")
        issues.append({
            'Check': 'Valid range',
            'File': 'trust_responses',
            'Issue': f'{item} has {count} values outside 1-5',
            'Severity': 'HIGH'
        })
else:
    print("\n✓ All Trust items within valid range (1-5)")

# Understanding items should be 1-5
understanding_items = [f'understanding_{i}' for i in range(1, 6)]
und_invalid = understanding[understanding_items].apply(lambda x: ((x < 1) | (x > 5)).sum())
if und_invalid.sum() > 0:
    print(f"\n❌ Understanding has {und_invalid.sum()} values outside 1-5:")
    for item, count in und_invalid[und_invalid > 0].items():
        print(f"   {item}: {count} invalid values")
        issues.append({
            'Check': 'Valid range',
            'File': 'understanding_responses',
            'Issue': f'{item} has {count} values outside 1-5',
            'Severity': 'HIGH'
        })
else:
    print("\n✓ All Understanding items within valid range (1-5)")

# Confidence items should be 1-5
confidence_items = [f'confidence_{i}' for i in range(1, 5)]
conf_invalid = confidence[confidence_items].apply(lambda x: ((x < 1) | (x > 5)).sum())
if conf_invalid.sum() > 0:
    print(f"\n❌ Confidence has {conf_invalid.sum()} values outside 1-5:")
    for item, count in conf_invalid[conf_invalid > 0].items():
        print(f"   {item}: {count} invalid values")
        issues.append({
            'Check': 'Valid range',
            'File': 'decision_confidence',
            'Issue': f'{item} has {count} values outside 1-5',
            'Severity': 'HIGH'
        })
else:
    print("\n✓ All Confidence items within valid range (1-5)")

# ============================================================================
# 3. STRAIGHT-LINING DETECTION
# ============================================================================

print("\n" + "=" * 80)
print("3. CHECKING FOR STRAIGHT-LINING (Same Response Across All Items)")
print("=" * 80)

def detect_straightlining(df, items, name):
    """Detect if all items have the same response for each row."""
    straightliners = []
    
    for idx, row in df.iterrows():
        values = row[items].values
        if len(set(values)) == 1:  # All values are the same
            straightliners.append({
                'participant_id': row['participant_id'],
                'condition': row.get('condition', 'N/A'),
                'value': values[0],
                'scale': name
            })
    
    return straightliners

# Check SUS
sus_straightline = detect_straightlining(sus, sus_items, 'SUS')
if sus_straightline:
    print(f"\n⚠️ {len(sus_straightline)} SUS responses show straight-lining:")
    for sl in sus_straightline:
        print(f"   {sl['participant_id']} ({sl['condition']}): all items = {sl['value']}")
        issues.append({
            'Check': 'Straight-lining',
            'File': 'sus_responses',
            'Issue': f"{sl['participant_id']} ({sl['condition']}): all items = {sl['value']}",
            'Severity': 'MEDIUM'
        })
else:
    print("\n✓ No straight-lining detected in SUS")

# Check Trust
trust_straightline = detect_straightlining(trust, trust_items, 'Trust')
if trust_straightline:
    print(f"\n⚠️ {len(trust_straightline)} Trust responses show straight-lining:")
    for sl in trust_straightline:
        print(f"   {sl['participant_id']} ({sl['condition']}): all items = {sl['value']}")
        issues.append({
            'Check': 'Straight-lining',
            'File': 'trust_responses',
            'Issue': f"{sl['participant_id']} ({sl['condition']}): all items = {sl['value']}",
            'Severity': 'MEDIUM'
        })
else:
    print("\n✓ No straight-lining detected in Trust")

# Check Understanding
und_straightline = detect_straightlining(understanding, understanding_items, 'Understanding')
if und_straightline:
    print(f"\n⚠️ {len(und_straightline)} Understanding responses show straight-lining:")
    for sl in und_straightline:
        print(f"   {sl['participant_id']} ({sl['condition']}): all items = {sl['value']}")
        issues.append({
            'Check': 'Straight-lining',
            'File': 'understanding_responses',
            'Issue': f"{sl['participant_id']} ({sl['condition']}): all items = {sl['value']}",
            'Severity': 'MEDIUM'
        })
else:
    print("\n✓ No straight-lining detected in Understanding")

# ============================================================================
# 4. SESSION DURATION CHECKS
# ============================================================================

print("\n" + "=" * 80)
print("4. CHECKING SESSION DURATIONS")
print("=" * 80)

# Calculate session duration per participant (across both conditions)
session_durations = []

for pid in demographics['participant_id']:
    # Get timestamps for this participant
    sus_times = sus[sus['participant_id'] == pid]['timestamp'].values
    qual_times = qualitative[qualitative['participant_id'] == pid]['timestamp'].values
    
    if len(sus_times) >= 2 and len(qual_times) > 0:
        # First SUS (start of Variant A) to qualitative feedback (end)
        try:
            start_time = pd.to_datetime(sus_times[0])
            end_time = pd.to_datetime(qual_times[0])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            
            session_durations.append({
                'participant_id': pid,
                'duration_minutes': duration_minutes
            })
        except:
            pass

if session_durations:
    df_durations = pd.DataFrame(session_durations)
    
    print(f"\nSession Duration Statistics (n={len(df_durations)}):")
    print(f"  Mean: {df_durations['duration_minutes'].mean():.1f} minutes")
    print(f"  Median: {df_durations['duration_minutes'].median():.1f} minutes")
    print(f"  Min: {df_durations['duration_minutes'].min():.1f} minutes")
    print(f"  Max: {df_durations['duration_minutes'].max():.1f} minutes")
    
    # Flag suspiciously short sessions (<10 min) or long sessions (>60 min)
    too_short = df_durations[df_durations['duration_minutes'] < 10]
    too_long = df_durations[df_durations['duration_minutes'] > 60]
    
    if len(too_short) > 0:
        print(f"\n⚠️ {len(too_short)} sessions < 10 minutes (possibly rushed):")
        for _, row in too_short.iterrows():
            print(f"   {row['participant_id']}: {row['duration_minutes']:.1f} min")
            issues.append({
                'Check': 'Session duration',
                'File': 'timestamps',
                'Issue': f"{row['participant_id']}: {row['duration_minutes']:.1f} min (< 10 min)",
                'Severity': 'LOW'
            })
    
    if len(too_long) > 0:
        print(f"\n⚠️ {len(too_long)} sessions > 60 minutes (possibly interrupted):")
        for _, row in too_long.iterrows():
            print(f"   {row['participant_id']}: {row['duration_minutes']:.1f} min")
            issues.append({
                'Check': 'Session duration',
                'File': 'timestamps',
                'Issue': f"{row['participant_id']}: {row['duration_minutes']:.1f} min (> 60 min)",
                'Severity': 'LOW'
            })
    
    if len(too_short) == 0 and len(too_long) == 0:
        print("\n✓ All session durations within reasonable range (10-60 min)")

# ============================================================================
# 5. MISSING DATA PATTERNS
# ============================================================================

print("\n" + "=" * 80)
print("5. CHECKING FOR MISSING DATA PATTERNS")
print("=" * 80)

# Check if every participant has both conditions
print("\nCondition completeness:")
for pid in demographics['participant_id']:
    sus_conditions = set(sus[sus['participant_id'] == pid]['condition'].values)
    
    if len(sus_conditions) < 2:
        print(f"   ⚠️ {pid}: missing condition(s) - has {sus_conditions}")
        issues.append({
            'Check': 'Missing conditions',
            'File': 'sus_responses',
            'Issue': f"{pid}: has only {sus_conditions} (should have both variant_a and variant_b)",
            'Severity': 'HIGH'
        })

print("\n✓ Missing data check complete")

# ============================================================================
# SAVE ISSUES REPORT
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    df_issues = pd.DataFrame(issues)
    df_issues.to_csv('results/data_quality/data_integrity_issues.csv', index=False)
    
    print(f"\n⚠️ Found {len(issues)} potential issues:")
    print(f"   HIGH severity: {len(df_issues[df_issues['Severity'] == 'HIGH'])}")
    print(f"   MEDIUM severity: {len(df_issues[df_issues['Severity'] == 'MEDIUM'])}")
    print(f"   LOW severity: {len(df_issues[df_issues['Severity'] == 'LOW'])}")
    print("\n✓ Saved: results/data_quality/data_integrity_issues.csv")
else:
    print("\n✅ NO ISSUES FOUND - Data integrity looks good!")
    
    # Save empty report
    pd.DataFrame(columns=['Check', 'File', 'Issue', 'Severity']).to_csv(
        'results/data_quality/data_integrity_issues.csv', index=False
    )
    print("✓ Saved: results/data_quality/data_integrity_issues.csv (no issues)")

print("=" * 80)
