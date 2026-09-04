import json
import os
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

CSV_FILE = "land_acquisition_data.csv"

# 1. Synthetic Dataset Generator (Self-healing fallback agar CSV missing ho)
def generate_synthetic_data(n_samples: int = 1200) -> pd.DataFrame:
    np.random.seed(42)
    stages = [
        "Section 11 (Notice)",
        "Section 15 (Hearing)",
        "Section 19 (Declaration)",
        "Section 23 (Enquiry/Award)",
        "Possession Taken",
    ]
    forest_statuses = ["Approved", "Pending", "Not Required"]

    records = []
    for _ in range(n_samples):
        stg = np.random.choice(stages, p=[0.25, 0.25, 0.25, 0.15, 0.10])
        days_elapsed = int(np.random.uniform(30, 360))
        statutory_left = max(5, 365 - days_elapsed + int(np.random.normal(0, 15)))
        khata_dispute = int(np.random.choice([0, 1], p=[0.65, 0.35]))
        court_stay = int(np.random.choice([0, 1], p=[0.82, 0.18]))
        forest = np.random.choice(forest_statuses, p=[0.40, 0.35, 0.25])
        circle_ratio = round(float(np.random.uniform(0.4, 0.95)), 2)
        disb_pct = round(float(np.random.uniform(0, 100)), 1) if stg != "Section 11 (Notice)" else round(float(np.random.uniform(0, 20)), 1)

        # Realistic statutory delay generation based on actual bottlenecks
        delay = 20.0
        if khata_dispute == 1:
            delay += 65.0
        if court_stay == 1:
            delay += 110.0
        if forest == "Pending":
            delay += 50.0
        if statutory_left < 45:
            delay += 75.0
        if disb_pct < 25.0:
            delay += 40.0
        elif disb_pct > 80.0:
            delay -= 25.0

        delay += np.random.normal(0, 10)
        delay = max(5, int(round(delay)))

        records.append({
            "stage": stg,
            "days_elapsed_sec11": days_elapsed,
            "statutory_days_left": statutory_left,
            "unpartitioned_khata": khata_dispute,
            "court_stay": court_stay,
            "forest_clearance": forest,
            "circle_to_market_ratio": circle_ratio,
            "disbursement_pct": disb_pct,
            "delay_days": delay
        })

    synthetic_df = pd.DataFrame(records)
    synthetic_df.to_csv(CSV_FILE, index=False)
    print(f"Generated and saved {n_samples} synthetic training records to '{CSV_FILE}'")
    return synthetic_df


# 2. Data Loading
if os.path.exists(CSV_FILE):
    print(f"Loading existing dataset from '{CSV_FILE}'...")
    df = pd.read_csv(CSV_FILE)
else:
    print(f"'{CSV_FILE}' not found. Generating high-fidelity domain dataset...")
    df = generate_synthetic_data()

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

# 3. Categorical Variables One-Hot Encoding
X_encoded = pd.get_dummies(
    X, columns=["stage", "forest_clearance"], drop_first=False
)
encoded_feature_names = list(X_encoded.columns)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42
)

# 4. XGBoost Model Training
model = XGBRegressor(
    n_estimators=160, 
    max_depth=5, 
    learning_rate=0.07, 
    subsample=0.85,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=" * 50)
print("Model Training Complete!")
print(f"Mean Absolute Error (MAE): {mae:.2f} days")
print(f"R2 Score: {r2:.3f}")
print("=" * 50)

# 5. SHAP Explainer
explainer = shap.TreeExplainer(model)

# 6. Export Model & Artifacts
artifacts = {
    "model": model,
    "explainer": explainer,
    "feature_names": encoded_feature_names,
    "raw_feature_cols": feature_cols,
}
joblib.dump(artifacts, "land_model.joblib")
print("Successfully serialized model & SHAP artifacts to 'land_model.joblib'")


# ==========================================
# 7. Validation Test Run
# ==========================================
def validate_plot(sample_dict):
    sample_df = pd.DataFrame([sample_dict])
    sample_encoded = pd.get_dummies(sample_df)

    for col in encoded_feature_names:
        if col not in sample_encoded.columns:
            sample_encoded[col] = 0
    sample_encoded = sample_encoded[encoded_feature_names]

    pred_delay = float(model.predict(sample_encoded)[0])
    shap_vals = explainer(sample_encoded).values[0]

    impacts = []
    for feat, imp in zip(encoded_feature_names, shap_vals):
        if imp > 0:
            impacts.append({"factor": feat, "impact_days": round(float(imp), 1)})

    impacts = sorted(impacts, key=lambda x: x["impact_days"], reverse=True)[:3]
    total_imp = sum(x["impact_days"] for x in impacts) or 1.0
    for itm in impacts:
        itm["contribution_pct"] = round((itm["impact_days"] / total_imp) * 100, 1)

    return {
        "predicted_delay_days": max(0, round(pred_delay)),
        "top_bottlenecks": impacts,
    }


critical_sample = {
    "stage": "Section 15 (Hearing)",
    "days_elapsed_sec11": 310,
    "statutory_days_left": 35,
    "unpartitioned_khata": 1,
    "court_stay": 1,
    "forest_clearance": "Pending",
    "circle_to_market_ratio": 0.55,
    "disbursement_pct": 15.0,
}

print("\nValidation Test Output:")
print(json.dumps(validate_plot(critical_sample), indent=2))