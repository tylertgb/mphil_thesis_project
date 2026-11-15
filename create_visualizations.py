"""
Visualizations for Chapter 4
============================
Creates:
1. Paired plots (before-after for H2-H4)
2. Correlation scatter (H1: Understanding ↔ Trust)
3. Distribution plots for normality checks (Appendix)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# Set plot style
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# Create output directories
Path("results/figures").mkdir(parents=True, exist_ok=True)
Path("results/appendix").mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("CREATING VISUALIZATIONS FOR CHAPTER 4")
print("=" * 80)

# Load data
df = pd.read_csv('data/clean/analysis_paired.csv')
n = len(df)

# ============================================================================
# 1. PAIRED PLOTS (H2-H4)
# ============================================================================

print("\n1. Creating paired plots (H2-H4)...")

measures = {
    'SUS': ('sus_A', 'sus_B', 'System Usability (SUS)', (0, 100)),
    'Trust': ('trust_A', 'trust_B', 'Trust in AI', (1, 5)),
    'Understanding': ('understanding_A', 'understanding_B', 'Understanding', (1, 5)),
    'Confidence': ('confidence_A', 'confidence_B', 'Decision Confidence', (1, 5))
}

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for idx, (measure_key, (var_a, var_b, title, ylim)) in enumerate(measures.items()):
    ax = axes[idx]
    
    # Individual participant lines
    for i in range(n):
        ax.plot([1, 2], [df[var_a].iloc[i], df[var_b].iloc[i]], 
               'o-', color='gray', alpha=0.3, linewidth=0.5)
    
    # Mean lines
    mean_a = df[var_a].mean()
    mean_b = df[var_b].mean()
    ax.plot([1, 2], [mean_a, mean_b], 'o-', color='red', linewidth=3, 
           markersize=10, label=f'Mean')
    
    # Styling
    ax.set_xlim(0.8, 2.2)
    ax.set_ylim(ylim)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Static (A)', 'Progressive (B)'])
    ax.set_ylabel(title)
    ax.set_title(f'{title}\n(n = {n})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add mean values as text
    ax.text(1, ylim[0] + (ylim[1]-ylim[0])*0.05, f'M = {mean_a:.2f}', 
           ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.text(2, ylim[0] + (ylim[1]-ylim[0])*0.05, f'M = {mean_b:.2f}', 
           ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('results/figures/figure_4_1_paired_comparisons.png', dpi=300, bbox_inches='tight')
plt.savefig('results/figures/figure_4_1_paired_comparisons.pdf', bbox_inches='tight')
plt.close()
print("✓ Saved: results/figures/figure_4_1_paired_comparisons.png/pdf")

# ============================================================================
# 2. CORRELATION SCATTER PLOT (H1)
# ============================================================================

print("\n2. Creating correlation scatter plot (H1)...")

fig, ax = plt.subplots(figsize=(8, 6))

# Scatter plot
ax.scatter(df['understanding_avg'], df['trust_avg'], 
          s=100, alpha=0.6, edgecolors='black', linewidth=0.5)

# Regression line
z = np.polyfit(df['understanding_avg'], df['trust_avg'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['understanding_avg'].min(), df['understanding_avg'].max(), 100)
ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Regression line')

# Calculate correlation
r, p_val = stats.pearsonr(df['understanding_avg'], df['trust_avg'])

# Styling
ax.set_xlabel('Understanding (participant average across conditions)')
ax.set_ylabel('Trust (participant average across conditions)')
ax.set_title(f'H1: Understanding ↔ Trust\nPearson r = {r:.3f}, p < .001 (n = {n})')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(1, 5)
ax.set_ylim(1, 5)

plt.tight_layout()
plt.savefig('results/figures/figure_4_2_understanding_trust_correlation.png', dpi=300, bbox_inches='tight')
plt.savefig('results/figures/figure_4_2_understanding_trust_correlation.pdf', bbox_inches='tight')
plt.close()
print("✓ Saved: results/figures/figure_4_2_understanding_trust_correlation.png/pdf")

# ============================================================================
# 3. DISTRIBUTION PLOTS (NORMALITY CHECKS) - APPENDIX
# ============================================================================

print("\n3. Creating distribution plots for normality checks...")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

diff_data = {
    'SUS': df['sus_B'] - df['sus_A'],
    'Trust': df['trust_B'] - df['trust_A'],
    'Understanding': df['understanding_B'] - df['understanding_A'],
    'Confidence': df['confidence_B'] - df['confidence_A']
}

for idx, (measure, diff) in enumerate(diff_data.items()):
    ax = axes[idx]
    
    # Histogram with KDE
    ax.hist(diff, bins=10, density=True, alpha=0.6, color='skyblue', edgecolor='black')
    
    # KDE overlay
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(diff)
    x_range = np.linspace(diff.min(), diff.max(), 100)
    ax.plot(x_range, kde(x_range), 'r-', linewidth=2, label='KDE')
    
    # Normal distribution overlay
    mu, sigma = diff.mean(), diff.std()
    x_norm = np.linspace(diff.min(), diff.max(), 100)
    ax.plot(x_norm, stats.norm.pdf(x_norm, mu, sigma), 'g--', linewidth=2, label='Normal')
    
    # Shapiro-Wilk test
    w_stat, p_val = stats.shapiro(diff)
    
    # Styling
    ax.set_xlabel(f'{measure} Difference (Progressive - Static)')
    ax.set_ylabel('Density')
    ax.set_title(f'{measure}\nShapiro-Wilk: W = {w_stat:.3f}, p = {p_val:.3f}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axvline(0, color='black', linestyle=':', linewidth=1, alpha=0.5)

plt.tight_layout()
plt.savefig('results/appendix/appendix_a_normality_distributions.png', dpi=300, bbox_inches='tight')
plt.savefig('results/appendix/appendix_a_normality_distributions.pdf', bbox_inches='tight')
plt.close()
print("✓ Saved: results/appendix/appendix_a_normality_distributions.png/pdf")

# ============================================================================
# 4. Q-Q PLOTS (NORMALITY CHECKS) - APPENDIX
# ============================================================================

print("\n4. Creating Q-Q plots for normality checks...")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for idx, (measure, diff) in enumerate(diff_data.items()):
    ax = axes[idx]
    
    # Q-Q plot
    stats.probplot(diff, dist="norm", plot=ax)
    
    # Shapiro-Wilk test result
    w_stat, p_val = stats.shapiro(diff)
    
    # Styling
    ax.set_title(f'{measure} Q-Q Plot\nShapiro-Wilk: W = {w_stat:.3f}, p = {p_val:.3f}')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/appendix/appendix_b_qq_plots.png', dpi=300, bbox_inches='tight')
plt.savefig('results/appendix/appendix_b_qq_plots.pdf', bbox_inches='tight')
plt.close()
print("✓ Saved: results/appendix/appendix_b_qq_plots.png/pdf")

print("\n" + "=" * 80)
print("VISUALIZATION CREATION COMPLETE")
print("=" * 80)
print("\nFigures saved to:")
print("  - results/figures/ (main figures for Chapter 4)")
print("  - results/appendix/ (normality checks for appendix)")
print("=" * 80)
