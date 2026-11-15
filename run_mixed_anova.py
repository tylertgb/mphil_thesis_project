"""
Mixed ANOVA Analysis - Counterbalanced Study Design
─────────────────────────────────────────────────────────────────────────────
Design:
  - Within-subjects:  Interface Type (Static vs Progressive)
  - Between-subjects: Presentation Order (AB vs BA)
  - DVs: Trust, SUS, Understanding, Decision Confidence

Outputs:
  - Mixed ANOVA table (F, df, p, η²p) for each DV
  - Mauchly's sphericity (N/A for 2 levels, automatically met)
  - Post-hoc paired comparisons
  - Full results table for thesis
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import pingouin as pg
from pathlib import Path
from scipy import stats

DATA_DIR = Path("study_data")
OUTPUT_DIR = Path("results/mixed_anova")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
demographics = pd.read_csv(DATA_DIR / "demographics.csv")
trust        = pd.read_csv(DATA_DIR / "trust_responses.csv")
sus          = pd.read_csv(DATA_DIR / "sus_responses.csv")
understanding= pd.read_csv(DATA_DIR / "understanding_responses.csv")
conf_raw     = pd.read_csv(DATA_DIR / "decision_confidence.csv")

# Aggregate decision confidence per participant per condition
conf = conf_raw.groupby(
    ['participant_id', 'condition', 'presentation_order']
)['confidence_mean'].mean().reset_index()

print("=" * 65)
print("  MIXED ANOVA ANALYSIS — COUNTERBALANCED DESIGN")
print("  Within: Interface Type  |  Between: Presentation Order")
print("=" * 65)

results_summary = []


def run_mixed_anova(data, dv_col, dv_label):
    """Run mixed ANOVA and return formatted results."""
    print(f"\n{'─'*65}")
    print(f"  DV: {dv_label}")
    print(f"{'─'*65}")

    # Rename for pingouin
    df = data[['participant_id', 'condition', 'presentation_order', dv_col]].copy()
    df.columns = ['participant_id', 'interface', 'order', 'score']

    # Descriptives
    desc = df.groupby('interface')['score'].agg(['mean','std','count']).round(3)
    desc.index = ['Progressive (B)', 'Static (A)']
    print(f"\nDescriptives:")
    print(desc.to_string())

    # Mixed ANOVA via pingouin
    aov = pg.mixed_anova(
        data=df,
        dv='score',
        within='interface',
        between='order',
        subject='participant_id'
    )

    print(f"\nMixed ANOVA Table:")
    print(aov[['Source','DF1','DF2','F','p_unc','np2']].round(4).to_string(index=False))

    # Extract key effects
    interface_row  = aov[aov['Source'] == 'interface'].iloc[0]
    order_row      = aov[aov['Source'] == 'order'].iloc[0]
    interaction_row= aov[aov['Source'] == 'Interaction'].iloc[0]

    F_int  = round(interface_row['F'], 3)
    p_int  = round(interface_row['p_unc'], 4)
    np2_int= round(interface_row['np2'], 3)
    df1_int= int(interface_row['DF1'])
    df2_int= int(interface_row['DF2'])

    F_ord  = round(order_row['F'], 3)
    p_ord  = round(order_row['p_unc'], 4)
    np2_ord= round(order_row['np2'], 3)

    F_ia   = round(interaction_row['F'], 3)
    p_ia   = round(interaction_row['p_unc'], 4)
    np2_ia = round(interaction_row['np2'], 3)

    # Significance labels
    def sig_label(p):
        if p < .001: return "***"
        if p < .01:  return "**"
        if p < .05:  return "*"
        return "ns"

    print(f"\nKey Effects:")
    print(f"  Interface Type:    F({df1_int},{df2_int}) = {F_int}, p = {p_int} {sig_label(p_int)}, η²p = {np2_int}")
    print(f"  Presentation Order: F = {F_ord}, p = {p_ord} {sig_label(p_ord)}, η²p = {np2_ord}")
    print(f"  Interaction:        F = {F_ia},  p = {p_ia} {sig_label(p_ia)}, η²p = {np2_ia}")

    # Means per condition
    m_static = df[df['interface'] == 'variant_a']['score'].mean()
    m_prog   = df[df['interface'] == 'variant_b']['score'].mean()
    sd_static= df[df['interface'] == 'variant_a']['score'].std()
    sd_prog  = df[df['interface'] == 'variant_b']['score'].std()

    # Paired t-test (effect size)
    wide = df.pivot_table(index='participant_id', columns='interface', values='score').reset_index()
    t, p_t = stats.ttest_rel(wide['variant_b'], wide['variant_a'])
    diff = wide['variant_b'] - wide['variant_a']
    cohen_d = round(diff.mean() / diff.std(), 3)

    # Interaction interpretation
    if p_ia < .05:
        ia_note = "⚠️  Significant interaction — effect varies by order"
    else:
        ia_note = "✅ No interaction — effect consistent across orders"

    print(f"\n  {ia_note}")
    print(f"  Cohen's d = {cohen_d}  |  Static: M={round(m_static,2)}, SD={round(sd_static,2)}  |  Progressive: M={round(m_prog,2)}, SD={round(sd_prog,2)}")

    # Store for summary table
    results_summary.append({
        'DV': dv_label,
        'Static M (SD)': f"{round(m_static,2)} ({round(sd_static,2)})",
        'Progressive M (SD)': f"{round(m_prog,2)} ({round(sd_prog,2)})",
        'F (interface)': f"F({df1_int},{df2_int})={F_int}",
        'p (interface)': p_int,
        'sig': sig_label(p_int),
        'η²p': np2_int,
        "Cohen's d": cohen_d,
        'F (order)': F_ord,
        'p (order)': p_ord,
        'F (interaction)': F_ia,
        'p (interaction)': p_ia,
        'Interaction': ia_note[:2]
    })

    return aov


# ── Run for each DV ────────────────────────────────────────────────────────────
aov_trust = run_mixed_anova(trust,         'trust_mean',         'Trust')
aov_sus   = run_mixed_anova(sus,           'sus_score',          'SUS (Usability)')
aov_und   = run_mixed_anova(understanding, 'understanding_mean', 'Understanding')
aov_conf  = run_mixed_anova(conf,          'confidence_mean',    'Decision Confidence')

# ── Summary Table ──────────────────────────────────────────────────────────────
print(f"\n\n{'='*65}")
print("  THESIS RESULTS TABLE — MIXED ANOVA SUMMARY")
print(f"{'='*65}\n")

summary_df = pd.DataFrame(results_summary)

for _, row in summary_df.iterrows():
    print(f"  {row['DV']}")
    print(f"    Static:      {row['Static M (SD)']}")
    print(f"    Progressive: {row['Progressive M (SD)']}")
    cohens = row["Cohen's d"]
    print(f"    Interface:   {row['F (interface)']}, p={row['p (interface)']} {row['sig']}, η²p={row['η²p']}, d={cohens}")
    print(f"    Order:       F={row['F (order)']}, p={row['p (order)']}")
    print(f"    Interaction: F={row['F (interaction)']}, p={row['p (interaction)']} {row['Interaction']}")
    print()

# Save summary to CSV
summary_df.to_csv(OUTPUT_DIR / "mixed_anova_summary.csv", index=False)
print(f"✅ Summary saved to: {OUTPUT_DIR / 'mixed_anova_summary.csv'}")

# ── Normality Check ────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("  NORMALITY CHECK (Shapiro-Wilk on difference scores)")
print(f"{'='*65}\n")

for data, dv_col, dv_label in [
    (trust, 'trust_mean', 'Trust'),
    (sus, 'sus_score', 'SUS'),
    (understanding, 'understanding_mean', 'Understanding'),
    (conf, 'confidence_mean', 'Decision Confidence')
]:
    wide = data.pivot_table(index='participant_id', columns='condition', values=dv_col).reset_index()
    if 'variant_a' in wide.columns and 'variant_b' in wide.columns:
        diff = wide['variant_b'] - wide['variant_a']
        stat, p = stats.shapiro(diff)
        normal = "✅ Normal" if p > .05 else "⚠️  Non-normal"
        print(f"  {dv_label}: W={round(stat,3)}, p={round(p,4)} → {normal}")

print(f"\n{'='*65}")
print("  ANALYSIS COMPLETE")
print(f"{'='*65}")
print(f"\n  Results saved to: {OUTPUT_DIR}/")
print(f"  Files: mixed_anova_summary.csv\n")
