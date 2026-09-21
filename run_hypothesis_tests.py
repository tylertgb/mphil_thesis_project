"""
Hypothesis testing for the SHAP interface study (H1-H4).

Replaces the partial example in THESIS_NOTES.md, which tested SUS (H2) and
Trust (H4) correctly, but was missing H3 (Decision Confidence) and had an
extra "Understanding between conditions" test that isn't one of the study's
four hypotheses. H1 (correlation) was also missing entirely.

Expects study_data_for_analysis.csv in wide format, one row per participant,
with columns:
    sus_variant_a, sus_variant_b
    trust_variant_a, trust_variant_b
    understanding_variant_a, understanding_variant_b
    decision_confidence_variant_a, decision_confidence_variant_b

Adjust column names below if your export uses different ones.
"""

import pandas as pd
import numpy as np
from scipy.stats import ttest_rel, wilcoxon, pearsonr, spearmanr, shapiro

ALPHA = 0.05
DATA_PATH = "study_data/study_data_for_analysis.csv"


def cohens_d_paired(a, b):
    """Effect size for a paired comparison: mean difference / SD of differences."""
    diff = np.asarray(a) - np.asarray(b)
    return diff.mean() / diff.std(ddof=1)


def describe(label, series):
    print(f"  {label}: M = {series.mean():.2f}, SD = {series.std(ddof=1):.2f}")


def paired_comparison(name, hypothesis, a, b):
    """
    Runs the proposal's stated protocol: paired t-test by default, falling
    back to Wilcoxon Signed-Rank if either condition's differences fail a
    normality check (Shapiro-Wilk, alpha = 0.05) - matching §3.7's
    'Paired T-tests (or Wilcoxon Signed-Rank tests for non-parametric data)'.
    """
    print(f"\n--- {hypothesis}: {name} ---")
    describe("Variant A (Static)", a)
    describe("Variant B (Progressive)", b)

    diff = a - b
    _, normality_p = shapiro(diff)

    if normality_p >= ALPHA:
        stat, p_val = ttest_rel(a, b)
        d = cohens_d_paired(a, b)
        print(f"  Paired t-test: t = {stat:.2f}, df = {len(a) - 1}, "
              f"p = {p_val:.4f}, Cohen's d = {d:.2f}")
    else:
        stat, p_val = wilcoxon(a, b)
        print(f"  Normality check failed (Shapiro-Wilk p = {normality_p:.4f}), "
              f"using Wilcoxon Signed-Rank")
        print(f"  Wilcoxon: W = {stat:.2f}, p = {p_val:.4f}")

    sig = "significant" if p_val < ALPHA else "not significant"
    print(f"  Result: {sig} at alpha = {ALPHA}")
    return p_val


def correlation_test(name, hypothesis, x, y):
    """
    Pearson correlation by default, falling back to Spearman if either
    variable fails a normality check - matching §3.7's
    'Pearson or Spearman correlation, depending on the distribution of the data'.
    """
    print(f"\n--- {hypothesis}: {name} ---")
    print(f"  n = {len(x)}")

    _, norm_x = shapiro(x)
    _, norm_y = shapiro(y)

    if norm_x >= ALPHA and norm_y >= ALPHA:
        r, p_val = pearsonr(x, y)
        print(f"  Pearson: r = {r:.3f}, p = {p_val:.4f}")
    else:
        r, p_val = spearmanr(x, y)
        print(f"  Normality check failed, using Spearman")
        print(f"  Spearman: rho = {r:.3f}, p = {p_val:.4f}")

    sig = "significant" if p_val < ALPHA else "not significant"
    print(f"  Result: {sig} at alpha = {ALPHA}")
    return r, p_val


def run_hypothesis_tests():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("HYPOTHESIS TESTS")
    print("=" * 60)

    # H2: Progressive disclosure will achieve higher usability (SUS)
    # than static.
    paired_comparison(
        "SUS (Usability)", "H2",
        df["sus_variant_a"], df["sus_variant_b"]
    )

    # H4: Progressive disclosure will report higher trust than static.
    paired_comparison(
        "Trust", "H4",
        df["trust_variant_a"], df["trust_variant_b"]
    )

    # H3: Progressive disclosure will result in higher decision
    # confidence than static.
    paired_comparison(
        "Decision Confidence", "H3",
        df["decision_confidence_variant_a"], df["decision_confidence_variant_b"]
    )

    # H1: Higher perceived understanding will be positively associated
    # with higher trust, regardless of interface format.
    #
    # "Regardless of format" is tested here by pooling both conditions'
    # observations (n = participants x 2). Each participant contributes
    # two points, so this isn't fully independent data - if you want the
    # more conservative version, average each participant's Understanding
    # and Trust across both conditions first (n = participants) and
    # correlate those instead. Both are reported below so you can choose
    # which to lead with in the thesis; if they tell the same story,
    # that itself is reassurance the pooled result isn't just an artifact
    # of within-participant repetition.
    pooled_understanding = pd.concat([
        df["understanding_variant_a"], df["understanding_variant_b"]
    ], ignore_index=True)
    pooled_trust = pd.concat([
        df["trust_variant_a"], df["trust_variant_b"]
    ], ignore_index=True)

    correlation_test(
        "Understanding <-> Trust (pooled, both conditions)", "H1",
        pooled_understanding, pooled_trust
    )

    participant_avg_understanding = df[
        ["understanding_variant_a", "understanding_variant_b"]
    ].mean(axis=1)
    participant_avg_trust = df[
        ["trust_variant_a", "trust_variant_b"]
    ].mean(axis=1)

    correlation_test(
        "Understanding <-> Trust (per-participant average, conservative)", "H1",
        participant_avg_understanding, participant_avg_trust
    )

    print("\n" + "=" * 60)
    print("All four hypotheses tested. See above for per-test results.")
    print("=" * 60)


if __name__ == "__main__":
    run_hypothesis_tests()
