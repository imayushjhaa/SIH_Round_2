import joblib
import pandas as pd
import shap
import xgboost as xgb
from prompt_pipeline import build_recommendation_prompt

# 1. Load trained ML model artifacts
model = joblib.load("risk_model.pkl")
feature_names = joblib.load("model_features.pkl")
explainer = shap.TreeExplainer(model)


def evaluate_project_dict(project_dict: dict) -> str:
    df_input = pd.DataFrame([project_dict])

    # Compute financial gap ratio feature
    comp_offered = float(df_input.get("comp_offered_lakhs", pd.Series([0.0])).iloc[0])
    comp_demanded = float(df_input.get("comp_demanded_lakhs", pd.Series([0.0])).iloc[0])
    df_input["comp_gap_ratio"] = (comp_demanded - comp_offered) / (comp_offered + 1e-5)
    df_input["comp_gap_ratio"] = df_input["comp_gap_ratio"].clip(lower=0.0)

    # One-hot encode categorical clearance columns
    cat_cols = [c for c in ["forest_clearance_status", "env_clearance_status"] if c in df_input.columns]
    if cat_cols:
        df_encoded = pd.get_dummies(df_input, columns=cat_cols, drop_first=False)
    else:
        df_encoded = df_input.copy()

    # Align columns to match model training schema exactly
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    X_sample = df_encoded[feature_names]

    # Predict Risk Score (0-100)
    risk_score = round(float(model.predict(X_sample)[0]), 1)

    # Extract Baseline Expected Value
    raw_base = explainer.expected_value
    base_value = float(raw_base[0]) if hasattr(raw_base, "__iter__") else float(raw_base)

    # Compute SHAP feature contributions
    shap_vals = explainer.shap_values(X_sample)
    drivers = []

    for idx, col_name in enumerate(feature_names):
        impact = shap_vals[0][idx]
        val = X_sample.iloc[0][col_name]

        if ("forest_clearance_status" in col_name or "env_clearance_status" in col_name) and val == 0:
            continue

        clean_name = (
            col_name.replace("forest_clearance_status_", "Forest Clearance: ")
            .replace("env_clearance_status_", "Env Clearance: ")
            .replace("_", " ")
            .title()
        )

        drivers.append({
            "feature": clean_name,
            "shap_impact": round(float(impact), 2),
            "raw_impact": float(impact),
            "feature_value": val,
        })

    sorted_drivers = sorted(drivers, key=lambda x: abs(x["raw_impact"]), reverse=True)[:5]
    project_name = project_dict.get("project_name", "Selected Project")

    return build_recommendation_prompt(project_name, risk_score, base_value, sorted_drivers)


def run_interactive_csv_selector(csv_path: str = "land_acquisition_data.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not locate '{csv_path}' in current directory.")
        return

    total_rows = len(df)
    print("\n" + "=" * 65)
    print(f"   LAND ACQUISITION EVALUATION ENGINE | {total_rows} PROJECTS LOADED")
    print("=" * 65)

    user_query = input("\nEnter Row Index or Search Term: ").strip()

    if user_query.isdigit():
        selected_idx = int(user_query)
        if 0 <= selected_idx < total_rows:
            _display_analysis(selected_idx, df.iloc[selected_idx].to_dict())
            return
        else:
            print(f"Index out of range! Enter a number between 0 and {total_rows - 1}.")
            return

    matches = df[
        df["project_name"].astype(str).str.contains(user_query, case=False, na=False) |
        df["state"].astype(str).str.contains(user_query, case=False, na=False)
    ]

    if len(matches) == 0:
        print(f"No projects found matching '{user_query}'.")
        return

    if len(matches) == 1:
        _display_analysis(matches.index[0], matches.iloc[0].to_dict())
    else:
        print(f"\nFound {len(matches)} matching projects:")
        for idx, row in matches.head(10).iterrows():
            print(f"  [{idx}] {row.get('project_name', f'Project #{idx}')} | State: {row.get('state', 'N/A')}")

        choice = input("\nEnter Row Index from list above: ").strip()
        if choice.isdigit() and int(choice) in matches.index:
            _display_analysis(int(choice), df.iloc[int(choice)].to_dict())


def _display_analysis(index: int, project_dict: dict):
    project_label = project_dict.get("project_name", f"Project Row #{index}")
    print("\n" + "=" * 65)
    print(f"  GENERATING RISK ANALYSIS FOR ROW [{index}]: {project_label}")
    print("=" * 65 + "\n")
    print(evaluate_project_dict(project_dict))


if __name__ == "__main__":
    run_interactive_csv_selector()