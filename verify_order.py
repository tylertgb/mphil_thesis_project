"""
Verify Order: Check if presentation order was counterbalanced
"""
import pandas as pd

sus = pd.read_csv('study_data/sus_responses.csv')
sus['timestamp'] = pd.to_datetime(sus['timestamp'])

print("=" * 80)
print("VERIFYING PRESENTATION ORDER")
print("=" * 80)

# Check order for all participants
order_summary = []

for pid in sorted(sus['participant_id'].unique()):
    p_data = sus[sus['participant_id'] == pid].sort_values('timestamp')
    
    if len(p_data) == 2:
        first = p_data.iloc[0]['condition']
        second = p_data.iloc[1]['condition']
        
        order_summary.append({
            'participant_id': pid,
            'first': first,
            'second': second,
            'order': f"{first} → {second}"
        })

df_order = pd.DataFrame(order_summary)

print(f"\nTotal participants with both conditions: {len(df_order)}")
print("\nOrder distribution:")
print(df_order['order'].value_counts())

# Check if anyone saw variant_b first
b_first = df_order[df_order['first'] == 'variant_b']
print(f"\nParticipants who saw Progressive (variant_b) FIRST: {len(b_first)}")

if len(b_first) > 0:
    print("  Participants:", list(b_first['participant_id']))
    print("\n✓ ORDER WAS COUNTERBALANCED")
else:
    print("\n⚠️ ORDER WAS FIXED - ALL participants saw Static (variant_a) first!")
    print("   This is a MAJOR LIMITATION - order and treatment are confounded.")

print("\nSample participant orders:")
for _, row in df_order.head(10).iterrows():
    print(f"  {row['participant_id']}: {row['order']}")

print("=" * 80)
