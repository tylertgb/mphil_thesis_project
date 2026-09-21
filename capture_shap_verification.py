"""
Capture SHAP Verification Output for Thesis Appendix
"""

import sys
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from scipy.special import logit

# Redirect output to file
output_file = Path("results/shap_verification_output.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)

# Load model artifacts
SAVE_DIR = Path("models/saved_models")
model = joblib.load(SAVE_DIR / "logistic_regression.pkl")
scaler = joblib.load(SAVE_DIR / "scaler.pkl")
with open(SAVE_DIR / "feature_names.json") as f:
    feature_names = json.load(f)

# Load test data
df = pd.read_csv("data/processed/final_model_dataset_v2.csv")
X = df.drop(columns=["target"])
y = df["target"]
X_clean = X[feature_names].dropna()

# Scale
X_scaled = scaler.transform(X_clean.iloc[:10])

print("=" * 80)
print("SHAP ADDITIVITY VERIFICATION FOR THESIS")
print("=" * 80)
print()
print("Testing the additivity property: sum(SHAP values) + expected_value ~= model(X)")
print("This verifies that SHAP values are computed correctly.")
print()
print("For logistic regression in log-odds space:")
print("  SHAP_sum + E[f(X)] should equal model log-odds output")
print("  Tolerance: < 0.01 (differences due to floating-point precision)")
print()
print("-" * 80)

# Compute SHAP using same method as model
import shap
explainer = shap.LinearExplainer(model, X_scaled[:1], feature_perturbation="interventional")
shap_values_raw = explainer.shap_values(X_scaled)

# Extract class 1 (Success) SHAP values
if isinstance(shap_values_raw, list):
    shap_values = shap_values_raw[1]
    expected_value = explainer.expected_value[1]
elif len(shap_values_raw.shape) == 3:
    shap_values = shap_values_raw[:, :, 1]
    expected_value = explainer.expected_value[1]
else:
    shap_values = shap_values_raw
    expected_value = explainer.expected_value

print(f"Expected value (base rate): {expected_value:.4f}")
print(f"Number of test samples: {len(X_scaled)}")
print()
print("Sample-by-sample verification:")
print()
print(f"{'Sample':<8} {'SHAP Sum':<12} {'Model Output':<12} {'Difference':<12} {'Status':<10}")
print("-" * 80)

# Verify each sample
all_pass = True
for i in range(len(X_scaled)):
    shap_sum = shap_values[i].sum() + expected_value
    prob = model.predict_proba(X_scaled[i:i+1])[0, 1]
    model_logodds = logit(np.clip(prob, 1e-10, 1 - 1e-10))
    diff = abs(shap_sum - model_logodds)
    status = "PASS" if diff < 0.01 else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{i:<8} {shap_sum:>11.4f} {model_logodds:>11.4f} {diff:>11.6f} {status:<10}")

print("-" * 80)
print()

if all_pass:
    print("VERIFICATION RESULT: ALL SAMPLES PASS")
    print()
    print("Interpretation:")
    print("  - SHAP values correctly decompose model predictions")
    print("  - Additivity property holds for all test samples")
    print("  - Implementation is mathematically sound")
else:
    print("VERIFICATION RESULT: SOME SAMPLES FAILED")
    print()
    print("Warning: SHAP computation may have issues")

print()
print("=" * 80)
print("This output can be included in Thesis Appendix B")
print("=" * 80)
