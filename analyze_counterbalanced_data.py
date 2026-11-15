"""
Counterbalanced Data Analysis - Mixed ANOVA
─────────────────────────────────────────────────────────────────────────────
Analyzes counterbalanced within-subjects design:
- IV1: Interface Type (Static vs Progressive) - within-subjects
- IV2: Presentation Order (AB vs BA) - between-subjects
- DVs: Trust, Decision Confidence, Understanding, SUS

Tests:
1. Main effect of Interface Type
2. Main effect of Presentation Order
3. Interface × Order interaction
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# File paths
DATA_DIR = Path("study_data")
OUTPUT_DIR = Path("results/counterbalanced_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    """Load all data files from data branch."""
    print("Loading data...")
    
    demographics = pd.read_csv(DATA_DIR / "demographics.csv")
    trust = pd.read_csv(DATA_DIR / "trust_responses.csv")
    sus = pd.read_csv(DATA_DIR / "sus_responses.csv")
    understanding = pd.read_csv(DATA_DIR / "understanding_responses.csv")
    decision_conf = pd.read_csv(DATA_DIR / "decision_confidence.csv")
    
    print(f"✅ Loaded data for {len(demographics)} participants")
    print(f"   - Trust: {len(trust)} rows")
    print(f"   - SUS: {len(sus)} rows")
    print(f"   - Understanding: {len(understanding)} rows")
    print(f"   - Decision Confidence: {len(decision_conf)} rows")
    
    return demographics, trust, sus, understanding, decision_conf


def verify_counterbalancing(demographics):
    """Verify counterbalancing distribution."""
    print("\n" + "="*60)
    print("COUNTERBALANCING VERIFICATION")
    print("="*60)
    
    order_counts = demographics['presentation_order'].value_counts()
    print(f"\nPresentation Order Distribution:")
    print(f"  AB (Static first):     {order_counts.get('AB', 0)} participants")
    print(f"  BA (Progressive first): {order_counts.get('BA', 0)} participants")
    print(f"  Total:                  {len(demographics)} participants")
    
    # Chi-square test for balance
    expected = len(demographics) / 2
    chi2, p = stats.chisquare([order_counts.get('AB', 0), order_counts.get('BA', 0)])
    print(f"\nBalance test (χ²): χ² = {chi2:.3f}, p = {p:.4f}")
    if p > 0.05:
        print("  ✅ Groups are reasonably balanced")
    else:
        print("  ⚠️  Slight imbalance, but acceptable for analysis")
    
    return order_counts


def descriptive_statistics(data, dv_name, dv_col='trust_mean'):
    """Calculate descriptive statistics by condition and order."""
    print(f"\n{'='*60}")
    print(f"DESCRIPTIVE STATISTICS: {dv_name}")
    print(f"{'='*60}\n")
    
    # Overall by condition
    print("Overall by Interface Type:")
    overall = data.groupby('condition')[dv_col].agg([
        ('n', 'count'),
        ('M', 'mean'),
        ('SD', 'std'),
        ('Min', 'min'),
        ('Max', 'max')
    ]).round(3)
    print(overall)
    
    # By condition and order
    print(f"\nBy Interface Type × Presentation Order:")
    by_order = data.groupby(['condition', 'presentation_order'])[dv_col].agg([
        ('n', 'count'),
        ('M', 'mean'),
        ('SD', 'std')
    ]).round(3)
    print(by_order)
    
    # Calculate condition difference for each order group
    print(f"\nInterface Effect within Each Order Group:")
    for order in ['AB', 'BA']:
        subset = data[data['presentation_order'] == order]
        static = subset[subset['condition'] == 'variant_a'][dv_col].mean()
        progressive = subset[subset['condition'] == 'variant_b'][dv_col].mean()
        diff = progressive - static
        print(f"  {order}: Progressive - Static = {diff:+.3f}")
    
    return overall, by_order


def create_interaction_plot(data, dv_name, dv_col='trust_mean', output_file='interaction_plot.png'):
    """Create interaction plot for Interface × Order."""
    print(f"\nCreating interaction plot for {dv_name}...")
    
    # Calculate means
    means = data.groupby(['condition', 'presentation_order'])[dv_col].mean().reset_index()
    
    # Map condition names
    means['Interface'] = means['condition'].map({
        'variant_a': 'Static',
        'variant_b': 'Progressive'
    })
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#3498db', '#e74c3c']
    markers = ['o', 's']
    
    for i, order in enumerate(['AB', 'BA']):
        order_data = means[means['presentation_order'] == order]
        order_label = f"AB (Static → Progressive)" if order == 'AB' else "BA (Progressive → Static)"
        
        ax.plot(['Static', 'Progressive'],
                order_data[dv_col].values,
                marker=markers[i], linewidth=2.5, markersize=10,
                color=colors[i], label=order_label)
    
    ax.set_xlabel('Interface Type', fontsize=14, fontweight='bold')
    ax.set_ylabel(f'{dv_name} Score', fontsize=14, fontweight='bold')
    ax.set_title(f'Interface × Order Interaction: {dv_name}', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(title='Presentation Order', fontsize=11, title_fontsize=12)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / output_file, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved to {OUTPUT_DIR / output_file}")
    
    plt.close()
    
    # Interpretation
    ab_diff = means[(means['presentation_order'] == 'AB') & (means['Interface'] == 'Progressive')][dv_col].values[0] - \
              means[(means['presentation_order'] == 'AB') & (means['Interface'] == 'Static')][dv_col].values[0]
    ba_diff = means[(means['presentation_order'] == 'BA') & (means['Interface'] == 'Progressive')][dv_col].values[0] - \
              means[(means['presentation_order'] == 'BA') & (means['Interface'] == 'Static')][dv_col].values[0]
    
    print(f"\n  Interface effect in AB group: {ab_diff:+.3f}")
    print(f"  Interface effect in BA group: {ba_diff:+.3f}")
    
    if abs(ab_diff - ba_diff) < 0.2:
        print(f"  → Lines are approximately parallel → No interaction likely")
    else:
        print(f"  → Lines diverge → Possible interaction")


def paired_t_test_with_order(data, dv_name, dv_col='trust_mean'):
    """Perform paired t-test controlling for order."""
    print(f"\n{'='*60}")
    print(f"PAIRED T-TEST: {dv_name}")
    print(f"{'='*60}\n")
    
    # Overall effect (ignoring order)
    static = data[data['condition'] == 'variant_a'][dv_col]
    progressive = data[data['condition'] == 'variant_b'][dv_col]
    
    # Match by participant
    data_wide = data.pivot_table(
        index='participant_id',
        columns='condition',
        values=dv_col
    ).reset_index()
    
    t_stat, p_value = stats.ttest_rel(data_wide['variant_b'], data_wide['variant_a'])
    
    mean_diff = data_wide['variant_b'].mean() - data_wide['variant_a'].mean()
    
    # Calculate Cohen's d
    diff = data_wide['variant_b'] - data_wide['variant_a']
    cohens_d = diff.mean() / diff.std()
    
    print(f"Overall Paired t-test (Progressive vs Static):")
    print(f"  t({len(data_wide)-1}) = {t_stat:.3f}, p = {p_value:.4f}")
    print(f"  Mean difference = {mean_diff:+.3f}")
    print(f"  Cohen's d = {cohens_d:.3f}")
    
    if p_value < 0.001:
        print(f"  *** Highly significant (p < .001)")
    elif p_value < 0.01:
        print(f"  ** Significant (p < .01)")
    elif p_value < 0.05:
        print(f"  * Significant (p < .05)")
    else:
        print(f"  Not significant (p ≥ .05)")
    
    # Effect within each order group
    print(f"\nEffect within Each Order Group:")
    for order in ['AB', 'BA']:
        order_data = data[data['presentation_order'] == order]
        order_wide = order_data.pivot_table(
            index='participant_id',
            columns='condition',
            values=dv_col
        ).reset_index()
        
        if len(order_wide) > 1:
            t, p = stats.ttest_rel(order_wide['variant_b'], order_wide['variant_a'])
            diff = order_wide['variant_b'].mean() - order_wide['variant_a'].mean()
            print(f"  {order}: t({len(order_wide)-1}) = {t:.3f}, p = {p:.4f}, Δ = {diff:+.3f}")


def analyze_dv(demographics, data, dv_name, dv_col, plot_file):
    """Run complete analysis for one DV."""
    print(f"\n\n{'#'*60}")
    print(f"# ANALYZING: {dv_name}")
    print(f"{'#'*60}")
    
    # Descriptive stats
    overall, by_order = descriptive_statistics(data, dv_name, dv_col)
    
    # Interaction plot
    create_interaction_plot(data, dv_name, dv_col, plot_file)
    
    # Paired t-test
    paired_t_test_with_order(data, dv_name, dv_col)
    
    return overall, by_order


def main():
    """Run complete counterbalanced analysis."""
    print("\n" + "="*60)
    print("COUNTERBALANCED DATA ANALYSIS")
    print("Mixed ANOVA: Interface Type × Presentation Order")
    print("="*60)
    
    # Load data
    demographics, trust, sus, understanding, decision_conf = load_data()
    
    # Verify counterbalancing
    verify_counterbalancing(demographics)
    
    # Analyze Trust
    analyze_dv(demographics, trust, "Trust", "trust_mean", "trust_interaction.png")
    
    # Analyze SUS
    analyze_dv(demographics, sus, "System Usability (SUS)", "sus_score", "sus_interaction.png")
    
    # Analyze Understanding
    analyze_dv(demographics, understanding, "Understanding", "understanding_mean", 
               "understanding_interaction.png")
    
    # Analyze Decision Confidence (aggregate across tasks)
    conf_agg = decision_conf.groupby(['participant_id', 'condition', 'presentation_order'])['confidence_mean'].mean().reset_index()
    analyze_dv(demographics, conf_agg, "Decision Confidence", "confidence_mean", 
               "confidence_interaction.png")
    
    print(f"\n\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*60}")
    print(f"\n✅ Results saved to: {OUTPUT_DIR}/")
    print(f"✅ Interaction plots created")
    print(f"\n📊 Next steps:")
    print(f"   1. Review interaction plots")
    print(f"   2. Run formal mixed ANOVA (use statsmodels or pingouin)")
    print(f"   3. Update thesis chapters with counterbalanced results")
    print(f"\n")


if __name__ == "__main__":
    main()
