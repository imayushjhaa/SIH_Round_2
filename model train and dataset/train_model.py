import joblib
import pandas as pd
import xgboost as xgb

df = pd.read_csv("land_acquisition_data.csv")

feature_cols = [
    "land_area_acres", "comp_offered_lakhs", "comp_demanded_lakhs",
    "litigation_cases", "title_dispute_count", "comp_disbursal_delay_months",
    "public_objections_count", "slao_officer_vacant",
    "forest_clearance_status", "env_clearance_status"
]

X = df[feature_cols].copy()
X["comp_gap_ratio"] = (X["comp_demanded_lakhs"] - X["comp_offered_lakhs"]) / (X["comp_offered_lakhs"] + 1e-5)
X["comp_gap_ratio"] = X["comp_gap_ratio"].clip(lower=0.0)

# One-hot encoding for categoricals
X = pd.get_dummies(X, columns=["forest_clearance_status", "env_clearance_status"], drop_first=False)
y = df["delay_risk_label"]

model = xgb.XGBRegressor(n_estimators=150, max_depth=5, learning_rate=0.05, random_state=42)
model.fit(X, y)

joblib.dump(model, "risk_model.pkl")
joblib.dump(X.columns.tolist(), "model_features.pkl")
print("Retrained XGBoost model saved with 10 feature inputs!")