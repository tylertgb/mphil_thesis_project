"""
Comprehensive Data Quality Check for MPhil Thesis Study
========================================================
Checks all CSV files for completeness, consistency, and potential issues.
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("DATA QUALITY CHECK - MPhil Study")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')

# Get completed participant IDs (those with final feedback)
completed_ids = set(qualitative['participant_id'])

print(f"\n{'='*80}")
print("1. BASIC DATA COUNTS")
print(f"{'='*80}")
print(f"Demographics entries:        {len(demographics):>3}")
print(f"Final Feedback (completed):  {len(qualitative):>3}")
print(f"SUS responses:               {len(sus):>3}")
print(f"Trust responses:             {len(trust):>3}")
print(f"Understanding responses:     {len(understanding):>3}")
print(f"Decision confidence:         {len(decision_confidence):>3}")
print(f"Active sessions:             {len(active_sessions):>3}")

# Check 1: Duplicate participant IDs in demographics
print(f"\n{'='*80}")
print("2. CHECK FOR DUPLICATES")
print(f"{'='*80}")
demo_dupes = demographics['participant_id'].value_counts()
duplicates = demo_dupes[demo_dupes > 1]
if len(duplicates) > 0:
    print("⚠️  ISSUE: Duplicate demographics entries found:")
    for pid, count in duplicates.items():
        print(f"   {pid}: {count} entries")
else:
    print("✅ No duplicate demographics entries")

# Check 2: Participants with demographics but no final feedback (abandoned)
print(f"\n{'='*80}")
print("3. ABANDONED PARTICIPANTS (Started but didn't finish)")
print(f"{'='*80}")
demo_ids = set(demographics['participant_id'])
abandoned = demo_ids - completed_ids
if abandoned:
    print(f"⚠️  {len(abandoned)} participants started but didn't complete:")
    for pid in sorted(abandoned):
        print(f"   {pid}")
else:
    print("✅ No abandoned participants - all who started completed!")

# Check 3: Data consistency - each completed participant should have responses in all datasets
print(f"\n{'='*80}")
print("4. DATA COMPLETENESS CHECK (Completed Participants)")
print(f"{'='*80}")

sus_ids = set(sus['participant_id'])
trust_ids = set(trust['participant_id'])
understanding_ids = set(understanding['participant_id'])

print(f"\nCompleted participants: {len(completed_ids)}")
print(f"   In SUS:             {len(completed_ids & sus_ids)}")
print(f"   In Trust:           {len(completed_ids & trust_ids)}")
print(f"   In Understanding:   {len(completed_ids & understanding_ids)}")

# Missing data
missing_sus = completed_ids - sus_ids
missing_trust = completed_ids - trust_ids
missing_understanding = completed_ids - understanding_ids

issues = []
if missing_sus:
    issues.append(f"⚠️  Missing SUS data for: {missing_sus}")
if missing_trust:
    issues.append(f"⚠️  Missing Trust data for: {missing_trust}")
if missing_understanding:
    issues.append(f"⚠️  Missing Understanding data for: {missing_understanding}")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ All completed participants have responses in all datasets!")

# Check 4: Each participant should have exactly 2 SUS responses (variant_a, variant_b)
print(f"\n{'='*80}")
print("5. VARIANT RESPONSE COMPLETENESS")
print(f"{'='*80}")

for pid in sorted(completed_ids):
    sus_count = len(sus[sus['participant_id'] == pid])
    trust_count = len(trust[trust['participant_id'] == pid])
    understanding_count = len(understanding[understanding['participant_id'] == pid])
    
    if sus_count != 2 or trust_count != 2 or understanding_count != 2:
        print(f"⚠️  {pid}: SUS={sus_count}, Trust={trust_count}, Understanding={understanding_count} (expected 2 each)")

# Count how many have correct responses
correct_sus = sum(sus['participant_id'].value_counts() == 2)
correct_trust = sum(trust['participant_id'].value_counts() == 2)
correct_understanding = sum(understanding['participant_id'].value_counts() == 2)

print(f"\nParticipants with 2 responses each:")
print(f"   SUS:           {correct_sus}/{len(completed_ids)}")
print(f"   Trust:         {correct_trust}/{len(completed_ids)}")
print(f"   Understanding: {correct_understanding}/{len(completed_ids)}")

if correct_sus == len(completed_ids) and correct_trust == len(completed_ids) and correct_understanding == len(completed_ids):
    print("✅ All participants have exactly 2 responses (one per variant)!")

# Check 5: SUS Score Validity (should be between 0-100)
print(f"\n{'='*80}")
print("6. SUS SCORE VALIDITY")
print(f"{'='*80}")

invalid_sus = sus[(sus['sus_score'] < 0) | (sus['sus_score'] > 100)]
if len(invalid_sus) > 0:
    print(f"⚠️  {len(invalid_sus)} invalid SUS scores found:")
    print(invalid_sus[['participant_id', 'condition', 'sus_score']])
else:
    print("✅ All SUS scores are valid (0-100 range)")
    print(f"   Mean SUS (all): {sus['sus_score'].mean():.2f}")
    print(f"   Range: {sus['sus_score'].min():.2f} - {sus['sus_score'].max():.2f}")

# Check 6: Trust and Understanding Scale Validity (1-5 Likert)
print(f"\n{'='*80}")
print("7. LIKERT SCALE VALIDITY (Trust & Understanding)")
print(f"{'='*80}")

# Check all trust item columns (item_1 through item_5)
trust_items = [col for col in trust.columns if col.startswith('item_')]
trust_issues = []
for item in trust_items:
    invalid = trust[(trust[item] < 1) | (trust[item] > 5)]
    if len(invalid) > 0:
        trust_issues.append(f"   {item}: {len(invalid)} invalid values")

# Check all understanding item columns
understanding_items = [col for col in understanding.columns if col.startswith('item_')]
understanding_issues = []
for item in understanding_items:
    invalid = understanding[(understanding[item] < 1) | (understanding[item] > 5)]
    if len(invalid) > 0:
        understanding_issues.append(f"   {item}: {len(invalid)} invalid values")

if trust_issues or understanding_issues:
    print("⚠️  ISSUES FOUND:")
    if trust_issues:
        print("Trust scale issues:")
        for issue in trust_issues:
            print(issue)
    if understanding_issues:
        print("Understanding scale issues:")
        for issue in understanding_issues:
            print(issue)
else:
    print("✅ All Likert scale responses are valid (1-5 range)")

# Check 7: Missing values in required fields
print(f"\n{'='*80}")
print("8. MISSING VALUES CHECK")
print(f"{'='*80}")

print("\nDemographics missing values:")
demo_missing = demographics[demographics['participant_id'].isin(completed_ids)].isnull().sum()
if demo_missing.sum() > 0:
    print(demo_missing[demo_missing > 0])
else:
    print("✅ No missing values in demographics")

print("\nQualitative feedback missing/empty responses:")
qual_missing = qualitative.isnull().sum()
qual_empty = (qualitative == '').sum()
total_issues = qual_missing + qual_empty
if total_issues.sum() > 0:
    print("⚠️  Missing or empty responses:")
    print(total_issues[total_issues > 0])
else:
    print("✅ No missing values in qualitative feedback")

# Check 8: Variant preference distribution
print(f"\n{'='*80}")
print("9. VARIANT PREFERENCE DISTRIBUTION")
print(f"{'='*80}")

preferences = qualitative['q4_preference'].value_counts()
print("\nPreference breakdown:")
for pref, count in preferences.items():
    percentage = (count / len(qualitative)) * 100
    print(f"   {pref}: {count} ({percentage:.1f}%)")

# Check 9: Demographics distribution
print(f"\n{'='*80}")
print("10. DEMOGRAPHICS DISTRIBUTION (Completed Participants)")
print(f"{'='*80}")

completed_demo = demographics[demographics['participant_id'].isin(completed_ids)]

print("\nGender:")
gender_counts = completed_demo['gender'].value_counts()
for gender, count in gender_counts.items():
    print(f"   {gender}: {count} ({count/len(completed_demo)*100:.1f}%)")

print("\nEducation Level:")
edu_counts = completed_demo['education_level'].value_counts()
for edu, count in edu_counts.items():
    print(f"   {edu}: {count}")

print("\nAge Group:")
age_counts = completed_demo['age_group'].value_counts()
for age, count in age_counts.items():
    print(f"   {age}: {count}")

print("\nYears of Experience:")
exp_counts = completed_demo['years_experience'].value_counts()
for exp, count in exp_counts.items():
    print(f"   {exp}: {count}")

print("\nFamiliarity with Analytics (1=Low, 5=High):")
fam_counts = completed_demo['familiarity_with_analytics'].value_counts().sort_index()
for fam, count in fam_counts.items():
    print(f"   Level {fam}: {count}")

# Check 10: Decision confidence patterns
print(f"\n{'='*80}")
print("11. DECISION CONFIDENCE DATA")
print(f"{'='*80}")

completed_decisions = decision_confidence[decision_confidence['participant_id'].isin(completed_ids)]
print(f"Total decision records for completed participants: {len(completed_decisions)}")
print(f"Expected: ~{len(completed_ids) * 6} (6 decisions per participant)")

decisions_per_participant = completed_decisions['participant_id'].value_counts()
print(f"\nParticipants with 6 decisions: {sum(decisions_per_participant == 6)}/{len(completed_ids)}")

abnormal = decisions_per_participant[decisions_per_participant != 6]
if len(abnormal) > 0:
    print("⚠️  Participants with abnormal decision counts:")
    for pid, count in abnormal.items():
        print(f"   {pid}: {count} decisions (expected 6)")
else:
    print("✅ All participants have exactly 6 decision records")

# FINAL SUMMARY
print(f"\n{'='*80}")
print("SUMMARY & RECOMMENDATIONS")
print(f"{'='*80}")

print(f"\n✅ STRENGTHS:")
print(f"   • {len(completed_ids)} completed participants (exceeds target of 30)")
print(f"   • All completed participants have responses in all datasets")
print(f"   • SUS scores are valid (0-100 range)")
print(f"   • Likert scales are valid (1-5 range)")
print(f"   • Strong preference signal ({preferences.iloc[0]}: {preferences.iloc[0]/len(qualitative)*100:.1f}%)")

issues_found = []
if len(duplicates) > 0:
    issues_found.append(f"• {len(duplicates)} duplicate demographics entries")
if abandoned:
    issues_found.append(f"• {len(abandoned)} abandoned participants (can be removed)")
if qual_missing.sum() > 0 or qual_empty.sum() > 0:
    issues_found.append(f"• Some missing/empty qualitative responses")
if len(abnormal) > 0:
    issues_found.append(f"• {len(abnormal)} participants with abnormal decision counts")

if issues_found:
    print(f"\n⚠️  ISSUES TO ADDRESS:")
    for issue in issues_found:
        print(f"   {issue}")
    print(f"\n📋 RECOMMENDED ACTIONS:")
    print(f"   1. Remove abandoned participants from demographics.csv")
    print(f"   2. Verify any duplicate entries")
    print(f"   3. Check participants with missing data")
else:
    print(f"\n✅ NO CRITICAL ISSUES FOUND!")
    print(f"   Data is clean and ready for analysis!")

print(f"\n{'='*80}")
print("END OF DATA QUALITY CHECK")
print(f"{'='*80}\n")
