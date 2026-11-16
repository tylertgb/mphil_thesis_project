"""
Investigate H1 flip: r=.799 → ρ=.037
─────────────────────────────────────
Checks:
1. Are participant IDs matched correctly between Understanding and Trust?
2. Are participant averages computed correctly?
3. What do the raw scores look like for 5 participants?
4. Where did the old r=.799 come from?
5. True paired t-test p-values for H2-H4
6. Preference breakdown by order group
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

DATA_DIR = Path("study_data")

trust = pd.read_csv(DATA_DIR / "trust_responses.csv")
sus   = pd.read_csv(DATA_DIR / "sus_responses.csv")
und   = pd.read_csv(DATA_DIR / "understanding_responses.csv")
conf  = pd.read_csv(DATA_DIR / "decision_confidence.csv")
dem   = pd.read_csv(DATA_DIR / "demographics.csv")
qual  = pd.read_csv(DATA_DIR / "qualitative_feedback.csv")

print("=" * 65)
print("TASK 1: INVESTIGATE H1 FLIP")
print("=" * 65)

# ── 1a. Row counts per file ────────────────────────────────────────
print("\n1a. Row counts:")
print(f"  demographics:   {len(dem)} rows")
print(f"  trust:          {len(trust)} rows")
print(f"  understanding:  {len(und)} rows")
print(f"  sus:            {len(sus)} rows")
print(f"  decision_conf:  {len(conf)} rows")

# ── 1b. Unique participant IDs per file ───────────────────────────
print("\n1b. Unique participant IDs per file:")
for name, df in [('trust', trust), ('understanding', und),
                 ('sus', sus), ('demographics', dem)]:
    ids = df['participant_id'].unique()
    print(f"  {name}: {len(ids)} unique IDs")

# ── 1c. Are the same IDs in trust and understanding? ─────────────
t_ids = set(trust['participant_id'].unique())
u_ids = set(und['participant_id'].unique())
print(f"\n1c. ID overlap trust ∩ understanding: {len(t_ids & u_ids)}")
print(f"  In trust not in understanding: {t_ids - u_ids}")
print(f"  In understanding not in trust: {u_ids - t_ids}")

# ── 1d. Compute participant averages STEP BY STEP ─────────────────
print("\n1d. Computing participant averages step by step:")

# Wide format
trust_w = trust.pivot_table(
    index='participant_id', columns='condition', values='trust_mean'
).reset_index()
und_w = und.pivot_table(
    index='participant_id', columns='condition', values='understanding_mean'
).reset_index()

print(f"  trust wide shape: {trust_w.shape}")
print(f"  und wide shape:   {und_w.shape}")

# Check columns
print(f"  trust wide columns: {trust_w.columns.tolist()}")
print(f"  und wide columns:   {und_w.columns.tolist()}")

# Compute averages
trust_w['trust_avg'] = trust_w[['variant_a', 'variant_b']].mean(axis=1)
und_w['und_avg']     = und_w[['variant_a', 'variant_b']].mean(axis=1)

# Merge
merged = und_w[['participant_id', 'und_avg']].merge(
         trust_w[['participant_id', 'trust_avg']], on='participant_id')

print(f"\n  Merged rows: {len(merged)}")
print(f"  Any NaN in und_avg: {merged['und_avg'].isna().sum()}")
print(f"  Any NaN in trust_avg: {merged['trust_avg'].isna().sum()}")

# ── 1e. Correlation both ways ─────────────────────────────────────
print("\n1e. Correlations on participant averages:")
r_p, p_p   = stats.pearsonr(merged['und_avg'], merged['trust_avg'])
rho_s, p_s = stats.spearmanr(merged['und_avg'], merged['trust_avg'])
print(f"  Pearson  r   = {r_p:.4f}, p = {p_p:.4f}")
print(f"  Spearman rho = {rho_s:.4f}, p = {p_s:.4f}")

# ── 1f. What does the OLD analysis have? ─────────────────────────
print("\n1f. RECONSTRUCTING OLD r=.799:")
print("  Old analysis used POOLED scores (n=62, treating each row")
print("  as independent) — this is what gave r=.799.")
print("  Let's check that:")
und_pool   = und[['participant_id', 'condition', 'understanding_mean']].copy()
trust_pool = trust[['participant_id', 'condition', 'trust_mean']].copy()
pool = und_pool.merge(trust_pool, on=['participant_id', 'condition'])
r_pool, p_pool = stats.pearsonr(pool['understanding_mean'], pool['trust_mean'])
rho_pool, p_rho_pool = stats.spearmanr(pool['understanding_mean'], pool['trust_mean'])
print(f"  Pooled Pearson  r   = {r_pool:.4f}, p = {p_pool:.6f}  ← this is the old r=.799")
print(f"  Pooled Spearman rho = {rho_pool:.4f}, p = {p_rho_pool:.6f}")
print(f"\n  ➜ Pooled n=62 inflates correlation because each participant")
print(f"    contributes 2 points. The correct n=31 average gives r={r_p:.3f}.")

# ── 1g. Hand-check 5 participants ────────────────────────────────
print("\n" + "=" * 65)
print("TASK 2: HAND-CHECK 5 PARTICIPANTS")
print("=" * 65)

sample_ids = dem['participant_id'].head(5).tolist()
print(f"\nChecking: {sample_ids}\n")
print(f"{'ID':<30} {'und_A':>6} {'und_B':>6} {'und_avg':>8} "
      f"{'tr_A':>6} {'tr_B':>6} {'tr_avg':>8} {'order':>5}")
print("-" * 85)

for pid in sample_ids:
    u_a = und[(und['participant_id']==pid) & (und['condition']=='variant_a')]['understanding_mean'].values
    u_b = und[(und['participant_id']==pid) & (und['condition']=='variant_b')]['understanding_mean'].values
    t_a = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_a')]['trust_mean'].values
    t_b = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_b')]['trust_mean'].values
    order = dem[dem['participant_id']==pid]['presentation_order'].values

    u_a = u_a[0] if len(u_a) else 'MISSING'
    u_b = u_b[0] if len(u_b) else 'MISSING'
    t_a = t_a[0] if len(t_a) else 'MISSING'
    t_b = t_b[0] if len(t_b) else 'MISSING'
    order = order[0] if len(order) else 'MISSING'

    u_avg = round((float(u_a)+float(u_b))/2, 3) if u_a != 'MISSING' else 'N/A'
    t_avg = round((float(t_a)+float(t_b))/2, 3) if t_a != 'MISSING' else 'N/A'

    print(f"{pid:<30} {str(u_a):>6} {str(u_b):>6} {str(u_avg):>8} "
          f"{str(t_a):>6} {str(t_b):>6} {str(t_avg):>8} {str(order):>5}")

# Verify AB/BA from timestamps
print("\n2b. Verifying AB/BA from timestamps (first variant_a vs variant_b timestamp):")
print(f"{'ID':<30} {'first_variant_a':>22} {'first_variant_b':>22} {'assigned':>8} {'correct?':>8}")
print("-" * 95)

for pid in sample_ids:
    t_a_time = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_a')]['timestamp'].values
    t_b_time = trust[(trust['participant_id']==pid) & (trust['condition']=='variant_b')]['timestamp'].values
    assigned = dem[dem['participant_id']==pid]['presentation_order'].values

    if len(t_a_time) and len(t_b_time):
        a_first = t_a_time[0]
        b_first = t_b_time[0]
        actual_first = 'AB' if a_first < b_first else 'BA'
        assigned_val = assigned[0] if len(assigned) else 'MISSING'
        match = '✅' if actual_first == assigned_val else '❌ MISMATCH'
        print(f"{pid:<30} {a_first:>22} {b_first:>22} {assigned_val:>8} {match:>8}")

print("\n" + "=" * 65)
print("TASK 3: TRUE PAIRED T-TEST p-VALUES for H2-H4")
print("=" * 65)

conf_agg = conf.groupby(['participant_id','condition'])['confidence_mean'].mean().reset_index()

sus_w   = sus.pivot_table(index='participant_id', columns='condition', values='sus_score').reset_index()
trust_w2= trust.pivot_table(index='participant_id', columns='condition', values='trust_mean').reset_index()
conf_w  = conf_agg.pivot_table(index='participant_id', columns='condition', values='confidence_mean').reset_index()

for label, df_w, val in [
    ('H2 SUS',        sus_w,    'sus_score'),
    ('H3 Confidence', conf_w,   'confidence_mean'),
    ('H4 Trust',      trust_w2, 'trust_mean'),
]:
    a = df_w['variant_a'].values
    b = df_w['variant_b'].values
    t_stat, p_t = stats.ttest_rel(b, a)
    diff = b - a
    W_sw, p_sw = stats.shapiro(diff)
    print(f"\n  {label}:")
    print(f"    Shapiro-Wilk diff: W={W_sw:.3f}, p={p_sw:.4f}")
    print(f"    Paired t-test: t({len(a)-1}) = {t_stat:.3f}, p = {p_t:.4f}")

# Holm correction
raw_ps = []
for _, df_w, _ in [('H2', sus_w, ''), ('H3', conf_w, ''), ('H4', trust_w2, '')]:
    a = df_w['variant_a'].values
    b = df_w['variant_b'].values
    _, p = stats.ttest_rel(b, a)
    raw_ps.append(p)

# Manual Holm
sorted_ps = sorted(enumerate(raw_ps), key=lambda x: x[1])
holm_ps = [None]*3
for rank, (orig_idx, p) in enumerate(sorted_ps):
    holm_ps[orig_idx] = min(1.0, p * (3 - rank))
# Enforce monotonicity
for i in range(1, 3):
    orig_sorted_idx = sorted_ps[i][0]
    prev_sorted_idx = sorted_ps[i-1][0]
    if holm_ps[orig_sorted_idx] < holm_ps[prev_sorted_idx]:
        holm_ps[orig_sorted_idx] = holm_ps[prev_sorted_idx]

print(f"\n  Holm-corrected p-values (paired t-test):")
for label, raw, holm in zip(['H2 SUS','H3 Conf','H4 Trust'], raw_ps, holm_ps):
    print(f"    {label}: raw p={raw:.4f}, Holm p={round(holm,4)}")

print("\n" + "=" * 65)
print("TASK 4+7: PREFERENCE BREAKDOWN BY ORDER GROUP")
print("=" * 65)

pref = qual[['participant_id','q4_preference']].copy()
pref = pref.merge(dem[['participant_id','presentation_order']], on='participant_id')
pref['preferred_progressive'] = pref['q4_preference'].str.contains('Progressive', case=False)

print("\nFull preference table:")
pt = pref.groupby(['presentation_order','preferred_progressive']).size().reset_index(name='count')
pt['Interface'] = pt['preferred_progressive'].map({True:'Progressive', False:'Static'})
print(pt[['presentation_order','Interface','count']].to_string(index=False))

ab_prog = pref[(pref['presentation_order']=='AB') & pref['preferred_progressive']].shape[0]
ab_stat = pref[(pref['presentation_order']=='AB') & ~pref['preferred_progressive']].shape[0]
ba_prog = pref[(pref['presentation_order']=='BA') & pref['preferred_progressive']].shape[0]
ba_stat = pref[(pref['presentation_order']=='BA') & ~pref['preferred_progressive']].shape[0]

print(f"\n  AB (Static first, n=16):       {ab_prog} Progressive, {ab_stat} Static")
print(f"  BA (Progressive first, n=15):  {ba_prog} Progressive, {ba_stat} Static")
print(f"\n  BA preferred Progressive (saw it FIRST): {ba_prog}/15 = {ba_prog/15:.1%}")
print(f"  AB preferred Progressive (saw it SECOND): {ab_prog}/16 = {ab_prog/16:.1%}")
print(f"\n  → {'Recency DOES NOT explain preference' if ba_prog > ab_prog else 'Recency may explain some preference'}")
print(f"    BA saw Progressive FIRST and {ba_prog}/15 still preferred it")
print(f"    AB saw Progressive SECOND and {ab_prog}/16 preferred it")
