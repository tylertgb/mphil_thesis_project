"""
Regenerate Figure 4.1 and Figure 4.2 — Counterbalanced Data
─────────────────────────────────────────────────────────────────────────────
Overwrites existing files in results/figures/ — no duplicates created.

Figure 4.1: Paired comparisons (Static vs Progressive) for all 4 DVs
            - Now shows H2 SUS as SIGNIFICANT
            - Significance markers updated

Figure 4.2: Understanding–Trust scatter
            - Now shows ρ=.037 (not old r=.799)
            - Correct per-condition and overall lines
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy import stats
from pathlib import Path

np.random.seed(42)

DATA_DIR   = Path("study_data")
FIGURE_DIR = Path("results/figures")
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
dem   = pd.read_csv(DATA_DIR / "demographics.csv")
trust = pd.read_csv(DATA_DIR / "trust_responses.csv")
sus   = pd.read_csv(DATA_DIR / "sus_responses.csv")
und   = pd.read_csv(DATA_DIR / "understanding_responses.csv")
conf  = pd.read_csv(DATA_DIR / "decision_confidence.csv")

conf_agg = conf.groupby(
    ['participant_id', 'condition', 'presentation_order']
)['confidence_mean'].mean().reset_index()

def get_wide(df, val_col):
    return df.pivot_table(
        index=['participant_id', 'presentation_order'],
        columns='condition', values=val_col
    ).reset_index()

trust_w = get_wide(trust,    'trust_mean')
sus_w   = get_wide(sus,      'sus_score')
und_w   = get_wide(und,      'understanding_mean')
conf_w  = get_wide(conf_agg, 'confidence_mean')

n = len(trust_w)

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4.1 — Paired Comparisons (overwrite existing)
# ══════════════════════════════════════════════════════════════════════════════
print("Generating Figure 4.1 — Paired Comparisons...")

measures = [
    ('SUS (Usability)', sus_w,   'sus_score',          0, 100,
     'F(1,29)=11.729, p=.002**\ndz=0.626'),
    ('Trust',           trust_w, 'trust_mean',         1, 5,
     'F(1,29)=6.684, p=.015*\ndz=0.469'),
    ('Decision\nConfidence', conf_w, 'confidence_mean',1, 5,
     'F(1,29)=7.012, p=.013*\ndz=0.484'),
    ('Perceived\nUnderstanding', und_w, 'understanding_mean', 1, 5,
     'F(1,29)=1.079, p=.308 ns\ndz=0.185'),
]

fig, axes = plt.subplots(1, 4, figsize=(16, 7))
fig.suptitle(
    'Figure 4.1: Paired Comparisons — Static vs Progressive Interface\n'
    '(n=31; counterbalanced design; AB=16, BA=15)',
    fontsize=13, fontweight='bold', y=1.01
)

colors_ab = '#3498db'  # blue  — AB group
colors_ba = '#e74c3c'  # red   — BA group
mean_color = '#2c3e50'

for ax, (label, df_w, _, ymin, ymax, stats_str) in zip(axes, measures):
    a = df_w['variant_a'].values
    b = df_w['variant_b'].values
    order = df_w['presentation_order'].values

    # Draw individual participant lines
    for i in range(n):
        col = colors_ab if order[i] == 'AB' else colors_ba
        ax.plot([0, 1], [a[i], b[i]],
                color=col, alpha=0.25, linewidth=1.0, zorder=1)
        ax.scatter([0, 1], [a[i], b[i]],
                   color=col, alpha=0.4, s=25, zorder=2)

    # Means
    m_a, m_b = a.mean(), b.mean()
    ax.plot([0, 1], [m_a, m_b],
            color=mean_color, linewidth=3.0, zorder=5,
            marker='D', markersize=9)

    # Error bars (95% CI)
    ci_a = stats.t.ppf(0.975, n-1) * a.std(ddof=1) / np.sqrt(n)
    ci_b = stats.t.ppf(0.975, n-1) * b.std(ddof=1) / np.sqrt(n)
    ax.errorbar([0, 1], [m_a, m_b], yerr=[ci_a, ci_b],
                fmt='none', color=mean_color, capsize=6,
                linewidth=2.0, zorder=6)

    # Significance annotation
    p_val = float(stats_str.split('p=')[1].split('\n')[0].replace('**','').replace('*','').replace(' ns',''))
    sig_color = '#27ae60' if p_val < .05 else '#95a5a6'
    ax.annotate('', xy=(1, m_b + (ymax-ymin)*0.07),
                xytext=(0, m_a + (ymax-ymin)*0.07),
                arrowprops=dict(arrowstyle='-', color=sig_color, lw=1.5))
    bracket_y = max(m_a, m_b) + (ymax - ymin) * 0.10
    ax.text(0.5, bracket_y, stats_str,
            ha='center', va='bottom', fontsize=7.5,
            color=sig_color, fontweight='bold' if p_val < .05 else 'normal')

    # Axis formatting
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Static\n(Variant A)', 'Progressive\n(Variant B)'],
                       fontsize=10)
    ax.set_ylabel(label, fontsize=11)
    ax.set_ylim(ymin - (ymax-ymin)*0.1, ymax + (ymax-ymin)*0.3)
    ax.set_xlim(-0.3, 1.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Mean labels
    ax.text(-0.18, m_a, f'M={m_a:.2f}', fontsize=8.5,
            color=mean_color, va='center', fontweight='bold')
    ax.text(1.08,  m_b, f'M={m_b:.2f}', fontsize=8.5,
            color=mean_color, va='center', fontweight='bold')

# Legend
legend_elements = [
    Line2D([0],[0], color=colors_ab, alpha=0.6, lw=2,
           label='AB: Static first (n=16)'),
    Line2D([0],[0], color=colors_ba, alpha=0.6, lw=2,
           label='BA: Progressive first (n=15)'),
    Line2D([0],[0], color=mean_color, lw=3, marker='D',
           markersize=8, label='Group mean ± 95% CI'),
]
fig.legend(handles=legend_elements, loc='lower center',
           ncol=3, fontsize=10, frameon=True,
           bbox_to_anchor=(0.5, -0.04))

plt.tight_layout()

# Overwrite existing files
for ext in ['png', 'pdf']:
    path = FIGURE_DIR / f"figure_4_1_paired_comparisons.{ext}"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved (overwritten): {path}")

plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4.2 — Understanding–Trust Scatter (overwrite existing)
# ══════════════════════════════════════════════════════════════════════════════
print("\nGenerating Figure 4.2 — Understanding–Trust Correlation...")

# Participant averages
und_w['und_avg']   = und_w[['variant_a','variant_b']].mean(axis=1)
trust_w['trust_avg'] = trust_w[['variant_a','variant_b']].mean(axis=1)
merged = und_w[['participant_id','und_avg','presentation_order']].merge(
         trust_w[['participant_id','trust_avg']], on='participant_id')

# Per-condition
und_a  = und[und['condition']  == 'variant_a']['understanding_mean'].values
und_b  = und[und['condition']  == 'variant_b']['understanding_mean'].values
trust_a = trust[trust['condition'] == 'variant_a']['trust_mean'].values
trust_b = trust[trust['condition'] == 'variant_b']['trust_mean'].values

rho_overall, p_overall = stats.spearmanr(merged['und_avg'], merged['trust_avg'])
r_a, p_a = stats.pearsonr(und_a, trust_a)
r_b, p_b = stats.pearsonr(und_b, trust_b)

fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
fig.suptitle(
    'Figure 4.2: Perceived Understanding vs Trust\n'
    '(Counterbalanced design; H1 not supported)',
    fontsize=13, fontweight='bold'
)

# Panel 1: Participant averages (PRIMARY)
ax = axes[0]
ab_mask = merged['presentation_order'] == 'AB'
ax.scatter(merged.loc[ab_mask,  'und_avg'],
           merged.loc[ab_mask,  'trust_avg'],
           color='#3498db', alpha=0.75, s=70, zorder=3,
           label='AB (Static first, n=16)')
ax.scatter(merged.loc[~ab_mask, 'und_avg'],
           merged.loc[~ab_mask, 'trust_avg'],
           color='#e74c3c', alpha=0.75, s=70, marker='s', zorder=3,
           label='BA (Progressive first, n=15)')

# Flat trend line (near-zero correlation)
x_range = np.linspace(merged['und_avg'].min()-0.1,
                      merged['und_avg'].max()+0.1, 100)
slope, intercept, _, _, _ = stats.linregress(merged['und_avg'], merged['trust_avg'])
ax.plot(x_range, slope * x_range + intercept,
        color='#2c3e50', lw=1.5, ls='--', alpha=0.6)

ax.set_xlabel('Perceived Understanding\n(participant average)', fontsize=10)
ax.set_ylabel('Trust\n(participant average)', fontsize=10)
ax.set_title(f'PRIMARY\nSpearman ρ = {rho_overall:.3f}, p = {p_overall:.3f}',
             fontsize=10, fontweight='bold',
             color='#95a5a6')
ax.legend(fontsize=8, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(alpha=0.3, linestyle='--')
ax.text(0.05, 0.05, 'Not significant\n(H1 not supported)',
        transform=ax.transAxes, fontsize=9,
        color='#e74c3c', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', alpha=0.8))

# Panel 2: Static condition
ax = axes[1]
ax.scatter(und_a, trust_a, color='#8e44ad', alpha=0.7, s=70, zorder=3)
x_range2 = np.linspace(und_a.min()-0.1, und_a.max()+0.1, 100)
slope2, int2, _, _, _ = stats.linregress(und_a, trust_a)
ax.plot(x_range2, slope2*x_range2+int2,
        color='#8e44ad', lw=1.5, ls='--', alpha=0.6)
ax.set_xlabel('Perceived Understanding', fontsize=10)
ax.set_ylabel('Trust', fontsize=10)
ax.set_title(f'Static Interface\nPearson r = {r_a:.3f}, p = {p_a:.3f}',
             fontsize=10, fontweight='bold', color='#95a5a6')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(alpha=0.3, linestyle='--')

# Panel 3: Progressive condition
ax = axes[2]
ax.scatter(und_b, trust_b, color='#27ae60', alpha=0.7, s=70, zorder=3)
x_range3 = np.linspace(und_b.min()-0.1, und_b.max()+0.1, 100)
slope3, int3, _, _, _ = stats.linregress(und_b, trust_b)
ax.plot(x_range3, slope3*x_range3+int3,
        color='#27ae60', lw=1.5, ls='--', alpha=0.6)
ax.set_xlabel('Perceived Understanding', fontsize=10)
ax.set_ylabel('Trust', fontsize=10)
ax.set_title(f'Progressive Interface\nPearson r = {r_b:.3f}, p = {p_b:.3f}',
             fontsize=10, fontweight='bold', color='#95a5a6')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(alpha=0.3, linestyle='--')

plt.tight_layout()

# Overwrite existing files
for ext in ['png', 'pdf']:
    path = FIGURE_DIR / f"figure_4_2_understanding_trust_correlation.{ext}"
    plt.savefig(path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved (overwritten): {path}")

plt.close()

print("\n✅ Both figures regenerated. No duplicates created.")
print(f"   Location: {FIGURE_DIR}/")
print(f"   figure_4_1_paired_comparisons.png/.pdf")
print(f"   figure_4_2_understanding_trust_correlation.png/.pdf")
