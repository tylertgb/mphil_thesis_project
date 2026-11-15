"""
Qualitative Data Export for Thematic Analysis
=============================================
Export open-ended responses in a format suitable for manual thematic coding.
"""

import pandas as pd
from pathlib import Path

# Create output directories
Path("results/qualitative").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("QUALITATIVE DATA EXPORT FOR THEMATIC CODING")
print("=" * 80)

# Load qualitative feedback
df_qual = pd.read_csv('study_data/qualitative_feedback.csv')
n = len(df_qual)

print(f"\nTotal participants: n = {n}")

# ============================================================================
# Extract all open-ended responses
# ============================================================================

# Check available columns
qual_columns = [col for col in df_qual.columns if not col in ['participant_id', 'q4_preference', 'timestamp']]

print(f"\nQualitative response fields: {len(qual_columns)}")
for col in qual_columns:
    print(f"  - {col}")

# ============================================================================
# Export for coding
# ============================================================================

# Format 1: Wide format - all responses in one row per participant
df_qual.to_csv('results/qualitative/qualitative_responses_wide.csv', index=False)
print("\n✓ Saved: results/qualitative/qualitative_responses_wide.csv")

# Format 2: Long format - one response per row (easier for coding software)
long_data = []

for idx, row in df_qual.iterrows():
    participant_id = row['participant_id']
    preference = row.get('q4_preference', 'Not specified')  # Preference is in q4_preference
    
    for col in qual_columns:
        response = row[col]
        
        # Only include non-empty responses
        if pd.notna(response) and str(response).strip() != '':
            long_data.append({
                'Participant_ID': participant_id,
                'Preference': preference,
                'Question': col,
                'Response': response,
                'Theme_1': '',  # Empty column for manual coding
                'Theme_2': '',  # Empty column for manual coding
                'Theme_3': '',  # Empty column for manual coding
                'Notes': ''     # Empty column for coding notes
            })

df_long = pd.DataFrame(long_data)
df_long.to_csv('results/qualitative/qualitative_responses_long_for_coding.csv', index=False)
print("✓ Saved: results/qualitative/qualitative_responses_long_for_coding.csv")

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("QUALITATIVE RESPONSE SUMMARY")
print("=" * 80)

response_counts = []

for col in qual_columns:
    non_empty = df_qual[col].notna().sum()
    empty = n - non_empty
    pct_responded = (non_empty / n) * 100
    
    print(f"\n{col}:")
    print(f"  Responses: {non_empty} ({pct_responded:.1f}%)")
    print(f"  No response: {empty}")
    
    response_counts.append({
        'Question': col,
        'n_Responses': non_empty,
        '% Responded': f"{pct_responded:.1f}%",
        'n_Empty': empty
    })

df_summary = pd.DataFrame(response_counts)
df_summary.to_csv('results/qualitative/qualitative_response_summary.csv', index=False)

print("\n✓ Saved: results/qualitative/qualitative_response_summary.csv")

# ============================================================================
# Preference-specific exports
# ============================================================================

print("\n" + "=" * 80)
print("PREFERENCE-SPECIFIC EXPORTS")
print("=" * 80)

# Export by preference group
for pref in df_qual['q4_preference'].unique():
    pref_group = df_qual[df_qual['q4_preference'] == pref]
    safe_name = pref.replace('/', '_').replace(' ', '_').replace('(', '').replace(')', '')
    filename = f"results/qualitative/qualitative_{safe_name}.csv"
    pref_group.to_csv(filename, index=False)
    print(f"✓ Saved: {filename} (n = {len(pref_group)})")

# ============================================================================
# Coding Instructions
# ============================================================================

print("\n" + "=" * 80)
print("THEMATIC CODING INSTRUCTIONS")
print("=" * 80)

instructions = """
RECOMMENDED THEMATIC ANALYSIS APPROACH:

1. **Choose a file for coding:**
   - Use qualitative_responses_long_for_coding.csv for coding software
   - Use qualitative_responses_wide.csv for reading/overview

2. **Inductive Coding Process:**
   a. **Familiarization**: Read all responses to get overall sense
   b. **Initial Coding**: Generate codes from the data (open coding)
   c. **Theme Development**: Group codes into themes
   d. **Review Themes**: Check themes work across the dataset
   e. **Define & Name**: Clearly define each theme
   f. **Write-up**: Produce analysis for thesis Chapter 4

3. **Recommended Tools:**
   - NVivo, ATLAS.ti, or MAXQDA (qualitative coding software)
   - Excel/Google Sheets (manual coding using the columns provided)
   - Dedoose (web-based, collaborative)

4. **What to Look For:**
   - Reasons for interface preference
   - Perceived strengths/weaknesses of each interface
   - Trust-related comments
   - Usability issues or suggestions
   - Understanding/comprehension mentions
   - Decision-making process descriptions
   - Comparison between interfaces

5. **Rigor & Trustworthiness:**
   - Consider inter-rater reliability (second coder for subset)
   - Keep audit trail of coding decisions
   - Include representative quotes in thesis
   - Report theme prevalence (n participants mentioning)

6. **Integration with Quantitative:**
   - Use qualitative themes to explain quantitative findings
   - Look for convergence/divergence
   - Identify unexpected themes not captured in surveys
"""

with open('results/qualitative/CODING_INSTRUCTIONS.txt', 'w') as f:
    f.write(instructions)

print("\n✓ Saved: results/qualitative/CODING_INSTRUCTIONS.txt")

print("\n" + "=" * 80)
print("QUALITATIVE EXPORT COMPLETE")
print("=" * 80)
print("\nFiles ready for manual thematic coding:")
print("  - qualitative_responses_long_for_coding.csv (recommended for coding)")
print("  - qualitative_responses_wide.csv (for overview)")
print("  - qualitative_response_summary.csv (response rates)")
print("  - Preference-specific files")
print("  - CODING_INSTRUCTIONS.txt")
print("=" * 80)
