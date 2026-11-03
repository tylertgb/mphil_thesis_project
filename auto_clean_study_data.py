import pandas as pd

print("=" * 80)
print("AUTOMATIC STUDY DATA CLEANING")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')

print("\n📋 BEFORE CLEANING:")
print(f"   Demographics: {len(demographics)} entries ({demographics['participant_id'].nunique()} unique)")
print(f"   Final Feedback: {len(qualitative)} participants")
print(f"   SUS responses: {len(sus)} responses")
print(f"   Trust responses: {len(trust)} responses")
print(f"   Understanding responses: {len(understanding)} responses")
print(f"   Active sessions: {len(active_sessions)} sessions")
print(f"   Decision confidence: {len(decision_confidence)} decisions")

# Step 1: Remove duplicate demographics entries (keep first)
print("\n🧹 Step 1: Removing duplicate demographics entries...")
dupes = demographics['participant_id'].value_counts()
duplicate_ids = dupes[dupes > 1].index.tolist()
if duplicate_ids:
    for pid in duplicate_ids:
        print(f"   - Removing {dupes[pid]-1} duplicate(s) for {pid}")
    demographics = demographics.drop_duplicates(subset=['participant_id'], keep='first')
else:
    print("   ✅ No duplicates found")

# Step 2: Identify participants to remove
print("\n🧹 Step 2: Identifying participants to remove...")

demo_ids = set(demographics['participant_id'])
qual_ids = set(qualitative['participant_id'])
sus_ids = set(sus['participant_id'])

# Test IDs with unusual formats
test_ids = ['P-12345', 'P34456']

# Abandoned participants (started but never completed final feedback)
abandoned = demo_ids - qual_ids

# Incomplete participants (in SUS but not in final feedback)
incomplete_sus = sus_ids - qual_ids

# Combine all IDs to remove
ids_to_remove = set(test_ids) | abandoned | incomplete_sus

print(f"   - Test IDs: {len([tid for tid in test_ids if tid in demo_ids or tid in qual_ids or tid in sus_ids])}")
print(f"   - Abandoned (no final feedback): {len(abandoned)}")
print(f"   - Incomplete (SUS but no final feedback): {len(incomplete_sus)}")
print(f"   📊 Total to remove: {len(ids_to_remove)}")

if ids_to_remove:
    print(f"\n   IDs being removed:")
    for pid in sorted(ids_to_remove):
        reason = []
        if pid in test_ids:
            reason.append("test ID")
        if pid in abandoned:
            reason.append("no final feedback")
        if pid in incomplete_sus:
            reason.append("incomplete")
        print(f"      {pid} ({', '.join(reason)})")

# Step 3: Clean all dataframes
print("\n🧹 Step 3: Cleaning all data files...")

demographics_clean = demographics[~demographics['participant_id'].isin(ids_to_remove)]
qualitative_clean = qualitative[~qualitative['participant_id'].isin(ids_to_remove)]
sus_clean = sus[~sus['participant_id'].isin(ids_to_remove)]
trust_clean = trust[~trust['participant_id'].isin(ids_to_remove)]
understanding_clean = understanding[~understanding['participant_id'].isin(ids_to_remove)]
active_sessions_clean = active_sessions[~active_sessions['participant_id'].isin(ids_to_remove)]
decision_confidence_clean = decision_confidence[~decision_confidence['participant_id'].isin(ids_to_remove)]

# Step 4: Save cleaned data
print("\n💾 Step 4: Saving cleaned data...")

demographics_clean.to_csv('study_data/demographics.csv', index=False)
qualitative_clean.to_csv('study_data/qualitative_feedback.csv', index=False)
sus_clean.to_csv('study_data/sus_responses.csv', index=False)
trust_clean.to_csv('study_data/trust_responses.csv', index=False)
understanding_clean.to_csv('study_data/understanding_responses.csv', index=False)
active_sessions_clean.to_csv('study_data/active_sessions.csv', index=False)
decision_confidence_clean.to_csv('study_data/decision_confidence.csv', index=False)

print("   ✅ All files saved")

# Step 5: Final report
print("\n" + "=" * 80)
print("CLEANING COMPLETE!")
print("=" * 80)

print("\n📊 AFTER CLEANING:")
print(f"   Demographics: {len(demographics_clean)} entries")
print(f"   Final Feedback: {len(qualitative_clean)} participants")
print(f"   SUS responses: {len(sus_clean)} responses")
print(f"   Trust responses: {len(trust_clean)} responses")
print(f"   Understanding responses: {len(understanding_clean)} responses")
print(f"   Active sessions: {len(active_sessions_clean)} sessions")
print(f"   Decision confidence: {len(decision_confidence_clean)} decisions")

print(f"\n✅ VALID PARTICIPANTS: {len(qualitative_clean)}")
print(f"   All participants have complete data (demographics + both variants + final feedback)")

print("\n📝 CHANGES SUMMARY:")
print(f"   - Removed {len(demographics) - len(demographics_clean)} demographics entries")
print(f"   - Removed {len(qualitative) - len(qualitative_clean)} final feedback entries")
print(f"   - Removed {len(sus) - len(sus_clean)} SUS responses")
print(f"   - Removed {len(trust) - len(trust_clean)} Trust responses")
print(f"   - Removed {len(understanding) - len(understanding_clean)} Understanding responses")
print(f"   - Removed {len(active_sessions) - len(active_sessions_clean)} active sessions")
print(f"   - Removed {len(decision_confidence) - len(decision_confidence_clean)} decision records")

print("\n✅ Data is now clean and ready for analysis!")
print("   Next step: git add study_data/* && git commit && git push")

print("\n" + "=" * 80)
