import pandas as pd

print("=" * 80)
print("STUDY DATA STATUS CHECK")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')

print("\n📋 CURRENT DATA COUNTS:")
print(f"   Demographics: {len(demographics)} entries ({demographics['participant_id'].nunique()} unique)")
print(f"   Final Feedback: {len(qualitative)} participants")
print(f"   SUS responses: {len(sus)} responses")
print(f"   Trust responses: {len(trust)} responses")
print(f"   Understanding responses: {len(understanding)} responses")
print(f"   Active sessions: {len(active_sessions)} sessions")
print(f"   Decision confidence: {len(decision_confidence)} decisions")

# Check for issues
print("\n" + "=" * 80)
print("DATA QUALITY ISSUES")
print("=" * 80)

# Issue 1: Duplicates
print("\n1️⃣ DUPLICATE DEMOGRAPHICS:")
dupes = demographics['participant_id'].value_counts()
duplicate_ids = dupes[dupes > 1]
if len(duplicate_ids) > 0:
    print(f"   ⚠️  Found {len(duplicate_ids)} participant(s) with duplicates:")
    for pid, count in duplicate_ids.items():
        print(f"      {pid}: {count} entries")
else:
    print("   ✅ No duplicates")

# Issue 2: Test IDs
print("\n2️⃣ TEST/INVALID IDs:")
test_ids = ['P-12345', 'P34456']
found_test_ids = []
for tid in test_ids:
    in_any = (tid in demographics['participant_id'].values or 
              tid in qualitative['participant_id'].values or 
              tid in sus['participant_id'].values)
    if in_any:
        found_test_ids.append(tid)
        print(f"   ⚠️  {tid} found in data")

if not found_test_ids:
    print("   ✅ No test IDs found")

# Issue 3: Abandoned participants
print("\n3️⃣ ABANDONED PARTICIPANTS (Demographics but no Final Feedback):")
demo_ids = set(demographics['participant_id'])
qual_ids = set(qualitative['participant_id'])
abandoned = demo_ids - qual_ids

if abandoned:
    print(f"   ⚠️  {len(abandoned)} participants started but didn't complete:")
    for pid in sorted(abandoned):
        print(f"      {pid}")
else:
    print("   ✅ No abandoned participants")

# Issue 4: Incomplete data
print("\n4️⃣ INCOMPLETE DATA (SUS/Trust but no Final Feedback):")
sus_ids = set(sus['participant_id'])
incomplete = sus_ids - qual_ids

if incomplete:
    print(f"   ⚠️  {len(incomplete)} participants have partial data:")
    for pid in sorted(incomplete):
        print(f"      {pid}")
else:
    print("   ✅ No incomplete data")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_issues = len(duplicate_ids) + len(found_test_ids) + len(abandoned) + len(incomplete)
all_problem_ids = set(duplicate_ids.index.tolist()) | set(found_test_ids) | abandoned | incomplete

print(f"\n📊 Total issues found: {total_issues}")
print(f"📊 Unique participant IDs with issues: {len(all_problem_ids)}")

if all_problem_ids:
    print(f"\n🧹 RECOMMENDED ACTION:")
    print(f"   Remove {len(all_problem_ids)} participant IDs from all datasets")
    print(f"   This will leave {len(qual_ids) - len(all_problem_ids & qual_ids)} valid participants")
    print(f"\n   IDs to remove: {sorted(all_problem_ids)}")
else:
    print(f"\n✅ DATA IS CLEAN!")
    print(f"   {len(qual_ids)} valid participants with complete data")

print("\n" + "=" * 80)
