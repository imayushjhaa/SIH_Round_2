import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)

df = pd.read_csv("land_acquisition_data.csv")
num_rows = len(df)

# Sector patterns for project names
sectors = [
    ("Highway Expansion", ["Highway", "Expressway", "Bypass Corridor"]),
    ("Freight Corridor", ["Railway Link", "Freight Corridor", "Rail Line"]),
    ("Power Transmission", ["Power Grid Line", "Transmission Tower Line"]),
    ("Metro Rail Transit", ["Metro Extension", "Urban Transit Corridor"]),
    ("Industrial Park", ["Industrial Zone", "SEZ Land Complex"]),
    ("Water Pipeline", ["Irrigation Canal", "Bulk Water Pipeline"])
]

new_project_names = []
for idx in range(num_rows):
    sec_type, keywords = sectors[idx % len(sectors)]
    kw = keywords[idx % len(keywords)]
    state_name = str(df.iloc[idx]["state"]).title()
    new_project_names.append(f"{kw} Project #{idx+1} ({state_name})")

df["project_name"] = new_project_names

# Add new bottleneck features
df["env_clearance_status"] = np.random.choice(
    ["APPROVED", "PENDING", "REJECTED"], size=num_rows, p=[0.50, 0.35, 0.15]
)
df["title_dispute_count"] = np.random.poisson(lam=2.5, size=num_rows)
df["comp_disbursal_delay_months"] = np.random.randint(0, 37, size=num_rows)
df["public_objections_count"] = np.random.randint(0, 120, size=num_rows)
df["slao_officer_vacant"] = np.random.choice([0, 1], size=num_rows, p=[0.75, 0.25])
df["litigation_cases"] = np.where(df["litigation_cases"].isna(), 0, df["litigation_cases"]).astype(int)

# Derived feature
df["comp_gap_ratio"] = (df["comp_demanded_lakhs"] - df["comp_offered_lakhs"]) / (df["comp_offered_lakhs"] + 1e-5)
df["comp_gap_ratio"] = df["comp_gap_ratio"].clip(lower=0.0)

# Multi-factor delay risk formula
base_noise = np.random.normal(loc=18.0, scale=2.5, size=num_rows)
forest_map = {"APPROVED": 0.0, "PENDING": 11.5, "REJECTED": 22.0}
env_map = {"APPROVED": 0.0, "PENDING": 9.5, "REJECTED": 18.0}

forest_risk = df["forest_clearance_status"].map(forest_map).fillna(0.0)
env_risk = df["env_clearance_status"].map(env_map).fillna(0.0)

calculated_risk = (
    base_noise 
    + forest_risk 
    + env_risk 
    + (df["litigation_cases"] * 4.0)
    + (df["title_dispute_count"] * 2.5)
    + (df["comp_disbursal_delay_months"] * 0.8)
    + (df["public_objections_count"] * 0.1)
    + (df["slao_officer_vacant"] * 12.0)
    + np.minimum(df["comp_gap_ratio"] * 8.5, 18.0)
)

df["delay_risk_label"] = np.clip(calculated_risk, 5.0, 95.0).round(2)

# Final export
final_columns = [
    "project_id", "project_name", "district", "state", "latitude", "longitude",
    "land_area_acres", "comp_offered_lakhs", "comp_demanded_lakhs",
    "litigation_cases", "title_dispute_count", "comp_disbursal_delay_months",
    "public_objections_count", "slao_officer_vacant",
    "forest_clearance_status", "env_clearance_status",
    "delay_risk_label", "source_portal"
]

df[final_columns].to_csv("land_acquisition_data.csv", index=False)
print("Dataset successfully enriched and saved to land_acquisition_data.csv!")