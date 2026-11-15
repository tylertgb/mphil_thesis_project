"""
Final Data Cleaning for MPhil Study
====================================
Removes abandoned participants and prepares dataset for analysis.
"""

import pandas as pd

print("=" * 80)
print("FINAL DATA CLEANING")
print("=" * 80)

# Load all data files
demographics = pd.read_csv('study_data/demographics.csv')
qualitative = pd.read_csv('study_data/qualitative_feedback.csv')
sus = pd.read_csv('study_data/sus_responses.csv')
trust = pd.read_csv('study_data/trust_responses.csv')
understanding = pd.read_csv('study_data/understanding_responses.csv')
decision_confidence = pd.read_csv('study_data/decision_confidence.csv')
active_sessions = pd.read_csv('study_data/active_sessions.csv')

print("\n📋 BEFORE CLEANING:")
print(f"   Demographics entries:        {len(demographics)}")
print(f"   Final Feedback (completed):  {len(qualitative)}")
print(f"   SUS responses:               {len(sus)}")
print(f"   Trust responses:             {len(trust)}")
print(f"   Understanding responses:     {len(understanding)}")
print(f"   Decision confidence:         {len(decision_confidence)}")
print(f"   Active sessions:             {len(active_sessions)}")

# Get completed participant IDs (those with final feedback)
completed_ids = set(qualitative['participant_id'])

print(f"\n✅ Completed participants: {len(completed_ids)}")

# Identify abandoned participants
demo_ids = set(demographics['participant_id'])
abandoned = demo_ids - completed_ids

print(f"\n🧹 CLEANING ACTIONS:")
print(f"\n1. Removing {len(abandoned)} abandoned participants from demographics:")
for pid in sorted(abandoned):
    print(f"   - {pid}")

# Clean demographics - keep only completed participants
demographics_clean = demographics[demographics['participant_id'].isin(completed_ids)]

# Verify other datasets (should already be clean, but double-check)
sus_clean = sus[sus['participant_id'].isin(completed_ids)]
trust_clean = trust[trust['participant_id'].isin(completed_ids)]
understanding_clean = understanding[understanding['participant_id'].isin(completed_ids)]
decision_confidence_clean = decision_confidence[decision_confidence['participant_id'].isin(completed_ids)]
active_sessions_clean = active_sessions[active_sessions['participant_id'].isin(completed_ids)]

# No changes to qualitative (already only completed participants)
qualitative_clean = qualitative.copy()

print(f"\n2. Verifying data consistency:")
print(f"   ✓ All datasets now contain only completed participants")

# Save cleaned data
print(f"\n💾 Saving cleaned datasets...")
demographics_clean.to_csv('study_data/demographics.csv', index=False)
qualitative_clean.to_csv('study_data/qualitative_feedback.csv', index=False)
sus_clean.to_csv('study_data/sus_responses.csv', index=False)
trust_clean.to_csv('study_data/trust_responses.csv', index=False)
understanding_clean.to_csv('study_data/understanding_responses.csv', index=False)
decision_confidence_clean.to_csv('study_data/decision_confidence.csv', index=False)
active_sessions_clean.to_csv('study_data/active_sessions.csv', index=False)

print("\n✅ AFTER CLEANING:")
print(f"   Demographics entries:        {len(demographics_clean)}")
print(f"   Final Feedback (completed):  {len(qualitative_clean)}")
print(f"   SUS responses:               {len(sus_clean)}")
print(f"   Trust responses:             {len(trust_clean)}")
print(f"   Understanding responses:     {len(understanding_clean)}")
print(f"   Decision confidence:         {len(decision_confidence_clean)}")
print(f"   Active sessions:             {len(active_sessions_clean)}")

print(f"\n📊 SUMMARY:")
print(f"   • Removed: {len(demographics) - len(demographics_clean)} demographics entries")
print(f"   • Removed: {len(decision_confidence) - len(decision_confidence_clean)} decision confidence records")
print(f"   • Final valid participants: {len(completed_ids)}")
print(f"   • All datasets now consistent!")

print("\n" + "=" * 80)
print("CLEANING COMPLETE - DATA READY FOR ANALYSIS!")
print("=" * 80)

# Special note about P_20261007_170406
print("\n⚠️  NOTE FOR ANALYSIS:")
print("   Participant P_20261007_170406 has incomplete data:")
print("   - Only completed Variant B (missing Variant A)")
print("   - Include in Variant B standalone analysis (n=32)")
print("   - Exclude from paired A vs B comparisons (n=31)")
print("\n" + "=" * 80 + "\n")
