import pandas as pd
import os

print("=" * 80)
print("STUDY DATA CLEANING SCRIPT")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')

print("\n📋 INITIAL DATA COUNTS:")
print(f"   Demographics: {len(demographics)} entries ({demographics['participant_id'].nunique()} unique)")
print(f"   Final Feedback: {len(qualitative)} participants")
print(f"   SUS responses: {len(sus)} responses")
print(f"   Trust responses: {len(trust)} responses")
print(f"   Understanding responses: {len(understanding)} responses")
print(f"   Active sessions: {len(active_sessions)} sessions")
print(f"   Decision confidence: {len(decision_confidence)} decisions")

# ISSUE 1: Check for duplicates in demographics
print("\n" + "=" * 80)
print("ISSUE 1: DUPLICATE DEMOGRAPHICS ENTRIES")
print("=" * 80)
dupes = demographics['participant_id'].value_counts()
duplicate_ids = dupes[dupes > 1].index.tolist()

if duplicate_ids:
    print(f"⚠️  Found {len(duplicate_ids)} participant(s) with duplicate demographics:")
    for pid in duplicate_ids:
        count = dupes[pid]
        print(f"   - {pid}: {count} entries")
        # Keep only the first entry
        dup_indices = demographics[demographics['participant_id'] == pid].index
        print(f"     Action: Keeping first entry, removing {count-1} duplicate(s)")
    
    # Remove duplicates (keep first occurrence)
    demographics = demographics.drop_duplicates(subset=['participant_id'], keep='first')
else:
    print("✅ No duplicate demographics entries found")

# ISSUE 2: Check for test/invalid participant IDs
print("\n" + "=" * 80)
print("ISSUE 2: TEST/INVALID PARTICIPANT IDs")
print("=" * 80)

test_ids = ['P-12345', 'P34456']  # Known test IDs with unusual formats

demographics_test = demographics[demographics['participant_id'].isin(test_ids)]
qualitative_test = qualitative[qualitative['participant_id'].isin(test_ids)]
sus_test = sus[sus['participant_id'].isin(test_ids)]
trust_test = trust[trust['participant_id'].isin(test_ids)]
understanding_test = understanding[understanding['participant_id'].isin(test_ids)]
active_sessions_test = active_sessions[active_sessions['participant_id'].isin(test_ids)]
decision_confidence_test = decision_confidence[decision_confidence['participant_id'].isin(test_ids)]

print("Checking test IDs: P-12345, P34456")
for tid in test_ids:
    in_demo = tid in demographics['participant_id'].values
    in_qual = tid in qualitative['participant_id'].values
    in_sus = tid in sus['participant_id'].values
    in_trust = tid in trust['participant_id'].values
    in_understanding = tid in understanding['participant_id'].values
    in_sessions = tid in active_sessions['participant_id'].values
    in_decisions = tid in decision_confidence['participant_id'].values
    
    print(f"\n{tid}:")
    print(f"   Demographics: {in_demo}")
    print(f"   Final Feedback: {in_qual}")
    print(f"   SUS: {in_sus}")
    print(f"   Trust: {in_trust}")
    print(f"   Understanding: {in_understanding}")
    print(f"   Active Sessions: {in_sessions}")
    print(f"   Decision Confidence: {in_decisions}")
    
    if in_qual:
        feedback = qualitative[qualitative['participant_id'] == tid]
        print(f"   Feedback preference: {feedback['q4_preference'].values[0]}")
        print(f"   Most useful: {feedback['q1_most_useful'].values[0][:50]}...")

# ISSUE 3: Check for abandoned participants (demographics but no final feedback)
print("\n" + "=" * 80)
print("ISSUE 3: ABANDONED PARTICIPANTS (Started but didn't complete)")
print("=" * 80)

demo_ids = set(demographics['participant_id'])
qual_ids = set(qualitative['participant_id'])
abandoned = demo_ids - qual_ids

print(f"Participants who started demographics but didn't submit final feedback: {len(abandoned)}")
if abandoned:
    print(f"IDs: {sorted(abandoned)}")
    print(f"\n⚠️  These participants have incomplete data and should be REMOVED")
else:
    print("✅ No abandoned participants")

# ISSUE 4: Check for participants in other datasets but not in qualitative (incomplete study)
print("\n" + "=" * 80)
print("ISSUE 4: PARTIAL COMPLETIONS (In SUS/Trust but no Final Feedback)")
print("=" * 80)

sus_ids = set(sus['participant_id'])
incomplete_sus = sus_ids - qual_ids

if incomplete_sus:
    print(f"⚠️  {len(incomplete_sus)} participant(s) in SUS but not in Final Feedback:")
    print(f"IDs: {sorted(incomplete_sus)}")
else:
    print("✅ All SUS participants completed the study")

# DECISION: What to clean
print("\n" + "=" * 80)
print("CLEANING DECISIONS")
print("=" * 80)

ids_to_remove = []

# Add test IDs if they exist
for tid in test_ids:
    if tid in demo_ids or tid in qual_ids or tid in sus_ids:
        ids_to_remove.append(tid)

# Add abandoned participants
ids_to_remove.extend(list(abandoned))

# Add incomplete participants
ids_to_remove.extend(list(incomplete_sus))

# Remove duplicates from removal list
ids_to_remove = list(set(ids_to_remove))

print(f"\nTotal participant IDs to REMOVE: {len(ids_to_remove)}")
if ids_to_remove:
    print(f"IDs: {sorted(ids_to_remove)}")
    print(f"\nReason: Test IDs, abandoned (no final feedback), or incomplete data")
else:
    print("✅ No IDs need to be removed")

# Show what will be kept
valid_participants = qual_ids - set(ids_to_remove)
print(f"\n✅ Valid participants to KEEP: {len(valid_participants)}")

# Ask for confirmation before cleaning
print("\n" + "=" * 80)
print("READY TO CLEAN DATA")
print("=" * 80)
print("\nThis script will:")
print(f"1. Remove {len(duplicate_ids)} duplicate demographics entries")
print(f"2. Remove {len(ids_to_remove)} participant IDs from all CSV files")
print(f"3. Keep {len(valid_participants)} valid participants who completed the study")

response = input("\nProceed with cleaning? (yes/no): ").strip().lower()

if response == 'yes':
    print("\n🧹 CLEANING DATA...")
    
    # Clean all dataframes
    demographics_clean = demographics[~demographics['participant_id'].isin(ids_to_remove)]
    qualitative_clean = qualitative[~qualitative['participant_id'].isin(ids_to_remove)]
    sus_clean = sus[~sus['participant_id'].isin(ids_to_remove)]
    trust_clean = trust[~trust['participant_id'].isin(ids_to_remove)]
    understanding_clean = understanding[~understanding['participant_id'].isin(ids_to_remove)]
    active_sessions_clean = active_sessions[~active_sessions['participant_id'].isin(ids_to_remove)]
    decision_confidence_clean = decision_confidence[~decision_confidence['participant_id'].isin(ids_to_remove)]
    
    # Save cleaned data
    demographics_clean.to_csv('study_data/demographics.csv', index=False)
    qualitative_clean.to_csv('study_data/qualitative_feedback.csv', index=False)
    sus_clean.to_csv('study_data/sus_responses.csv', index=False)
    trust_clean.to_csv('study_data/trust_responses.csv', index=False)
    understanding_clean.to_csv('study_data/understanding_responses.csv', index=False)
    active_sessions_clean.to_csv('study_data/active_sessions.csv', index=False)
    decision_confidence_clean.to_csv('study_data/decision_confidence.csv', index=False)
    
    print("\n✅ DATA CLEANED!")
    print("\n📊 FINAL DATA COUNTS:")
    print(f"   Demographics: {len(demographics_clean)} entries")
    print(f"   Final Feedback: {len(qualitative_clean)} participants")
    print(f"   SUS responses: {len(sus_clean)} responses")
    print(f"   Trust responses: {len(trust_clean)} responses")
    print(f"   Understanding responses: {len(understanding_clean)} responses")
    print(f"   Active sessions: {len(active_sessions_clean)} sessions")
    print(f"   Decision confidence: {len(decision_confidence_clean)} decisions")
    
    print("\n✅ All files saved. Ready to commit to Git!")
    
else:
    print("\n❌ Cleaning cancelled. No changes made.")

print("\n" + "=" * 80)
