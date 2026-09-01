import json
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Reproducibility ke liye seed
np.random.seed(42)
random.seed(42)

NUM_RECORDS = 1500

villages = [
    "Rampur",
    "Kalyanpur",
    "Bhatinda Khurd",
    "Mehrauli Dehat",
    "Sultanpur",
    "Fatehpur",
    "Shahpur",
]
projects = [
    "NH-44 Expansion",
    "Delhi-Amritsar Expressway",
    "Dedicated Freight Corridor",
    "PMGSY Phase-3 Link Road",
]
stages = [
    "Section 11 (Notice)",
    "Section 15 (Hearing)",
    "Section 19 (Declaration)",
    "Award Enquiry",
    "Possession Taken",
]

data = []

base_date = datetime(2025, 1, 1)

for i in range(1, NUM_RECORDS + 1):
    khasra_no = f"KH-{random.randint(100, 999)}/{random.randint(1, 9)}"
    village = random.choice(villages)
    project = random.choice(projects)
    stage = random.choice(stages)

    # Section 11 Notification Date
    sec_11_days_ago = random.randint(15, 450)
    sec_11_date = base_date - timedelta(days=sec_11_days_ago)

    # Statutory deadline: 365 days from Section 11 for Section 19
    statutory_deadline_days_left = 365 - sec_11_days_ago

    # Ground Bottleneck Features
    unpartitioned_khata = np.random.choice([0, 1], p=[0.65, 0.35])
    court_stay = np.random.choice([0, 1], p=[0.88, 0.12])
    forest_clearance = np.random.choice(
        ["Not Required", "Approved", "Pending"], p=[0.50, 0.30, 0.20]
    )
    circle_to_market_ratio = round(random.uniform(0.4, 1.1), 2)

    # Financial velocity
    if stage in ["Section 11 (Notice)", "Section 15 (Hearing)"]:
        disbursement_pct = 0.0
    elif stage == "Possession Taken":
        disbursement_pct = 100.0
    else:
        disbursement_pct = (
            round(random.uniform(5.0, 40.0), 1)
            if unpartitioned_khata
            else round(random.uniform(30.0, 95.0), 1)
        )

    # Delay Logic (Ground Truth Calculation for Training)
    base_delay = 0
    if unpartitioned_khata == 1:
        base_delay += random.randint(90, 180)
    if court_stay == 1:
        base_delay += random.randint(150, 300)
    if forest_clearance == "Pending":
        base_delay += random.randint(60, 120)
    if circle_to_market_ratio < 0.6:
        base_delay += random.randint(45, 90)
    if (
        statutory_deadline_days_left < 45
        and stage == "Section 11 (Notice)"
        and base_delay > 30
    ):
        base_delay += 100  # Statutory lapsing risk penalty

    delay_days = max(0, int(base_delay + random.normalvariate(0, 15)))

    # Risk Tier classification
    if delay_days < 30:
        risk_tier = "Low"
    elif delay_days < 90:
        risk_tier = "Medium"
    elif delay_days < 180:
        risk_tier = "High"
    else:
        risk_tier = "Critical"

    # Status color code for Map
    if stage == "Possession Taken" or risk_tier == "Low":
        status_color = "green"
    elif risk_tier in ["Medium"]:
        status_color = "yellow"
    else:
        status_color = "red"

    record = {
        "khasra_no": khasra_no,
        "village": village,
        "project": project,
        "stage": stage,
        "sec_11_date": sec_11_date.strftime("%Y-%m-%d"),
        "days_elapsed_sec11": sec_11_days_ago,
        "statutory_days_left": statutory_deadline_days_left,
        "unpartitioned_khata": int(unpartitioned_khata),
        "court_stay": int(court_stay),
        "forest_clearance": forest_clearance,
        "circle_to_market_ratio": circle_to_market_ratio,
        "disbursement_pct": disbursement_pct,
        "delay_days": delay_days,
        "risk_tier": risk_tier,
        "status_color": status_color,
    }
    data.append(record)

# 1. Export Full Dataset to CSV for ML Training
df = pd.DataFrame(data)
df.to_csv("land_acquisition_data.csv", index=False)
print("Saved 1500 rows to land_acquisition_data.csv")

# 2. Export 25 mock parcels to JSON for Frontend Dev
mock_frontend_data = data[:25]
with open("mockData.json", "w") as f:
    json.dump(mock_frontend_data, f, indent=2)
print("Saved 25 items to mockData.json for Frontend team")