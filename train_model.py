import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# 1. Load Data
df = pd.read_csv("land_acquisition_data.csv")

# Feature selection
feature_cols = [
    "stage",
    "days_elapsed_sec11",
    "statutory_days_left",
    "unpartitioned_khata",
    "court_stay",
    "forest_clearance",
    "circle_to_market_ratio",
    "disbursement_pct",
]

target_col = "delay_days"

X = df[feature_cols].copy()
y = df[target_col]

# 2. Categorical variables ko encode karo (One-Hot Encoding)
X_encoded = pd.get_dummies(
    X, columns=["stage", "forest_clearance"], drop_first=False
)
encoded_feature_names = list(X_encoded.columns)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42
)

# 3. XGBoost Model Training
model = XGBRegressor(
    n_estimators=150, max_depth=5, learning_rate=0.08, random_state=42
)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=" * 45)
print(f"Model Training Complete!")
print(f"Mean Absolute Error (MAE): {mae:.2f} days")
print(f"R2 Score: {r2:.3f}")
print("=" * 45)

# 4. SHAP Explainer Initialize karo
explainer = shap.TreeExplainer(model)

# 5. Export Model & Artifacts
artifacts = {
    "model": model,
    "explainer": explainer,
    "feature_names": encoded_feature_names,
    "raw_feature_cols": feature_cols,
}
joblib.dump(artifacts, "land_model.joblib")
print("Saved model artifacts to 'land_model.joblib'")


# ==========================================
# 6. Test Inference & SHAP Function (Sample)
# ==========================================
def explain_single_plot(sample_dict):
    """Ye function FastAPI backend me exact use hoga"""
    artifacts_loaded = joblib.load("land_model.joblib")
    xgb_model = artifacts_loaded["model"]
    tree_explainer = artifacts_loaded["explainer"]
    expected_cols = artifacts_loaded["feature_names"]

    # Input ko format karo
    sample_df = pd.DataFrame([sample_dict])
    sample_encoded = pd.get_dummies(sample_df)

    # Missing columns handle karo
    for col in expected_cols:
        if col not in sample_encoded.columns:
            sample_encoded[col] = 0
    sample_encoded = sample_encoded[expected_cols]

    # Predict delay days
    predicted_delay = float(xgb_model.predict(sample_encoded)[0])

    # SHAP values compute karo
    shap_values = tree_explainer(sample_encoded)
    values = shap_values.values[0]

    # Positive impacts nikaalo (jo delay badha rahe hain)
    impacts = []
    for feat_name, impact in zip(expected_cols, values):
        if impact > 0:  # Sirf wo jo delay create kar rahe hain
            impacts.append(
                {"factor": feat_name, "impact_days": round(float(impact), 1)}
            )

    # Sort by impact
    impacts = sorted(impacts, key=lambda x: x["impact_days"], reverse=True)[:3]

    total_impact = sum([x["impact_days"] for x in impacts]) or 1.0
    for item in impacts:
        item["contribution_pct"] = round(
            (item["impact_days"] / total_impact) * 100, 1
        )

    return {
        "predicted_delay_days": max(0, round(predicted_delay)),
        "top_bottlenecks": impacts,
    }


# Ek critical plot test karte hain:
sample_test = {
    "stage": "Section 11 (Notice)",
    "days_elapsed_sec11": 340,
    "statutory_days_left": 25,
    "unpartitioned_khata": 1,
    "court_stay": 1,
    "forest_clearance": "Pending",
    "circle_to_market_ratio": 0.5,
    "disbursement_pct": 10.0,
}

print("\nRunning Sample SHAP Explanation Test:")
result = explain_single_plot(sample_test)
import json

print(json.dumps(result, indent=2))