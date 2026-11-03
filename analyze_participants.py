import pandas as pd

# Read all CSV files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')

print("=" * 80)
print("PARTICIPANT ANALYSIS SUMMARY")
print("=" * 80)

# Demographics Analysis
print("\n📊 DEMOGRAPHICS:")
print(f"   Total entries: {len(demographics)}")
print(f"   Unique participants: {demographics['participant_id'].nunique()}")
duplicate_demos = demographics['participant_id'].value_counts()
if (duplicate_demos > 1).any():
    print(f"   ⚠️  Duplicates found:")
    for pid, count in duplicate_demos[duplicate_demos > 1].items():
        print(f"      - {pid}: {count} entries")

# Final Feedback (Study Completion)
print(f"\n✅ FINAL FEEDBACK (Completed Full Study):")
print(f"   Total submissions: {len(qualitative)}")
print(f"   Unique participants: {qualitative['participant_id'].nunique()}")

# Variant Preferences
print(f"\n🎯 VARIANT PREFERENCES (from Final Feedback):")
preferences = qualitative['q4_preference'].value_counts()
for pref, count in preferences.items():
    print(f"   {pref}: {count} ({count/len(qualitative)*100:.1f}%)")

# Active Sessions
print(f"\n📋 ACTIVE SESSIONS:")
print(f"   Total sessions: {len(active_sessions)}")
completed_both = active_sessions[(active_sessions['variant_a_completed'] == True) & 
                                  (active_sessions['variant_b_completed'] == True)]
print(f"   Completed both variants: {len(completed_both)}")
print(f"   Completed only Variant A: {len(active_sessions[active_sessions['variant_a_completed'] == True]) - len(completed_both)}")
print(f"   Completed only Variant B: {len(active_sessions[active_sessions['variant_b_completed'] == True]) - len(completed_both)}")

# SUS Responses
print(f"\n📝 SUS RESPONSES:")
print(f"   Total responses: {len(sus)}")
print(f"   Unique participants: {sus['participant_id'].nunique()}")
sus_by_condition = sus.groupby('condition')['participant_id'].nunique()
print(f"   Responses per condition:")
for condition, count in sus_by_condition.items():
    print(f"      {condition}: {count} participants")

# Trust Responses
print(f"\n🤝 TRUST RESPONSES:")
print(f"   Total responses: {len(trust)}")
print(f"   Unique participants: {trust['participant_id'].nunique()}")
trust_by_condition = trust.groupby('condition')['participant_id'].nunique()
print(f"   Responses per condition:")
for condition, count in trust_by_condition.items():
    print(f"      {condition}: {count} participants")

# Understanding Responses
print(f"\n💡 UNDERSTANDING RESPONSES:")
print(f"   Total responses: {len(understanding)}")
print(f"   Unique participants: {understanding['participant_id'].nunique()}")
understanding_by_condition = understanding.groupby('condition')['participant_id'].nunique()
print(f"   Responses per condition:")
for condition, count in understanding_by_condition.items():
    print(f"      {condition}: {count} participants")

# Decision Confidence
print(f"\n🎲 DECISION CONFIDENCE:")
print(f"   Total decisions recorded: {len(decision_confidence)}")
print(f"   Unique participants: {decision_confidence['participant_id'].nunique()}")

# Demographics Breakdown
print("\n" + "=" * 80)
print("PARTICIPANT DEMOGRAPHICS BREAKDOWN")
print("=" * 80)

print(f"\n👥 GENDER:")
gender_counts = demographics['gender'].value_counts()
for gender, count in gender_counts.items():
    print(f"   {gender}: {count} ({count/len(demographics)*100:.1f}%)")

print(f"\n🎓 EDUCATION LEVEL:")
edu_counts = demographics['education_level'].value_counts()
for edu, count in edu_counts.items():
    print(f"   {edu}: {count}")

print(f"\n💼 ROLE:")
role_counts = demographics['role'].value_counts()
for role, count in role_counts.items():
    print(f"   {role}: {count}")

print(f"\n📅 AGE GROUP:")
age_counts = demographics['age_group'].value_counts()
for age, count in age_counts.items():
    print(f"   {age}: {count}")

print(f"\n⏱️ YEARS OF EXPERIENCE:")
exp_counts = demographics['years_experience'].value_counts()
for exp, count in exp_counts.items():
    print(f"   {exp}: {count}")

print(f"\n📊 FAMILIARITY WITH ANALYTICS (1=Low, 5=High):")
fam_counts = demographics['familiarity_with_analytics'].value_counts().sort_index()
for fam, count in fam_counts.items():
    print(f"   Level {fam}: {count}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

total_complete = len(qualitative)
print(f"\n✅ Valid completed participants: {total_complete}")

if total_complete < 15:
    print(f"⚠️  Sample size is SMALL (n={total_complete})")
    print(f"   Recommended minimum: 15-20 participants for HCI study")
    print(f"   Need approximately: {15 - total_complete} more participants")
elif total_complete < 20:
    print(f"✓ Sample size is ACCEPTABLE (n={total_complete})")
    print(f"   Recommended for stronger results: {20 - total_complete} more participants")
else:
    print(f"✅ Sample size is GOOD (n={total_complete})")
    print(f"   Sufficient for within-subjects HCI comparison study")

print("\n" + "=" * 80)
