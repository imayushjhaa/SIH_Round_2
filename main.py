import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from pydantic import BaseModel
import shap
from prompt_pipeline import generate_dynamic_mitigation_steps

app = FastAPI(title="SIH26017 Land Acquisition Analytics Engine")

# Frontend cross-origin requests allow karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Load ML Artifacts & Data
artifacts = joblib.load("land_model.joblib")
model = artifacts["model"]
explainer = artifacts["explainer"]
expected_cols = artifacts["feature_names"]

with open("mockData.json", "r") as f:
    mock_list = json.load(f)
    raw_plots = {item["khasra_no"]: item for item in mock_list}


# 2. Prescriptive Recommendation Engine (Administrative Rules)
def get_prescriptive_action(top_factor: str, plot: dict) -> dict:
    if "unpartitioned_khata" in top_factor:
        return {
            "category": "Revenue & Mutation",
            "action_title": "Schedule Special DLSA Lok Adalat Camp",
            "recommended_officer": "Sub-Divisional Magistrate (SDM) / Tehsildar",
            "description": f"Plot {plot.get('khasra_no')} in village {plot.get('village')} has multi-heir succession gridlock. Conduct village-level on-spot mutation camp to clear account ownership.",
            "urgency": "High",
        }
    elif "court_stay" in top_factor:
        return {
            "category": "Litigation",
            "action_title": "File Urgent Motion for Vacation of Stay",
            "recommended_officer": "Government Pleader / CALA Legal Cell",
            "description": "High Court / Land Acquisition Authority stay is active. File counter-affidavit prioritizing infrastructure public interest under Section 25.",
            "urgency": "Critical",
        }
    elif "forest_clearance" in top_factor:
        return {
            "category": "Inter-Departmental Clearance",
            "action_title": "MoEFCC Nodal Officer Direct Escalation",
            "recommended_officer": "District Forest Officer (DFO)",
            "description": "Tree felling and forest land handover clearance is pending. Coordinate compensatory afforestation deposit release.",
            "urgency": "Medium",
        }
    elif "statutory_days_left" in top_factor:
        return {
            "category": "Statutory Compliance",
            "action_title": "Issue Emergency Section 19 Gazette Notification",
            "recommended_officer": "District Magistrate (DM)",
            "description": "Plot is approaching the 365-day statutory expiration limit under RFCTLARR Section 19(7). Gazette must be signed within 15 days to prevent legal lapse.",
            "urgency": "Immediate / Critical",
        }
    else:
        return {
            "category": "Financial Disbursement",
            "action_title": "PFMS Direct Benefit Transfer Drive",
            "recommended_officer": "Competent Authority for Land Acquisition (CALA)",
            "description": "Expedite award compensation transfer via PFMS bulk disbursement to accelerate physical land possession.",
            "urgency": "Medium",
        }


# ==========================================
# API Endpoints
# ==========================================


# Endpoint 1: GeoJSON Map Data (Real Farmland Coordinates)
@app.get("/api/parcels")
def get_parcels():
    plots_list = list(raw_plots.values())[:25]
    base_lat = 28.7510
    base_lng = 76.9150
    features = []
    grid_cols = 5

    for idx, plot in enumerate(plots_list):
        row = idx // grid_cols
        col = idx % grid_cols

        # Khet rectangular strip dimensions
        w = 0.0016
        h = 0.0011

        min_lng = base_lng + (col * w)
        max_lng = min_lng + (w * 0.92)
        min_lat = base_lat + (row * h)
        max_lat = min_lat + (h * 0.90)

        polygon_coords = [
            [
                [round(min_lng, 6), round(min_lat, 6)],
                [round(max_lng, 6), round(min_lat, 6)],
                [round(max_lng, 6), round(max_lat, 6)],
                [round(min_lng, 6), round(max_lat, 6)],
                [round(min_lng, 6), round(min_lat, 6)],
            ]
        ]

        features.append(
            {
                "type": "Feature",
                "id": plot["khasra_no"],
                "properties": {
                    "khasra_no": plot["khasra_no"],
                    "village": plot["village"],
                    "project": plot["project"],
                    "stage": plot["stage"],
                    "risk_tier": plot["risk_tier"],
                    "delay_days": plot["delay_days"],
                    "status_color": plot["status_color"],
                    "statutory_days_left": plot["statutory_days_left"],
                    "disbursement_pct": plot["disbursement_pct"],
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": polygon_coords,
                },
            }
        )

    return {"type": "FeatureCollection", "features": features}


# Endpoint 2: High-level Watchdog Dashboard Metrics
@app.get("/api/dashboard/summary")
def get_summary():
    plots_list = list(raw_plots.values())
    total_parcels = len(plots_list)
    critical_lapsing = sum(
        1
        for p in plots_list
        if p["statutory_days_left"] < 45 and p["stage"] != "Possession Taken"
    )
    high_risk = sum(
        1 for p in plots_list if p["risk_tier"] in ["High", "Critical"]
    )
    avg_disbursement = round(
        sum(p["disbursement_pct"] for p in plots_list) / total_parcels, 1
    )

    return {
        "total_parcels": total_parcels,
        "critical_lapsing_parcels": critical_lapsing,
        "high_risk_parcels": high_risk,
        "avg_disbursement_pct": avg_disbursement,
        "active_corridor": "Delhi-Amritsar Expressway (Sector 4)",
    }


# Endpoint 3: Specific Plot Details + SHAP Explanation + Prescriptive Action + GenAI Ground Plan
@app.get("/api/plot/{khasra_no:path}")
def get_plot_details(khasra_no: str):
    if khasra_no not in raw_plots:
        raise HTTPException(status_code=404, detail="Plot not found")

    plot = raw_plots[khasra_no]

    # Model inference
    sample_df = pd.DataFrame([plot])
    sample_encoded = pd.get_dummies(sample_df)
    for col in expected_cols:
        if col not in sample_encoded.columns:
            sample_encoded[col] = 0
    sample_encoded = sample_encoded[expected_cols]

    predicted_delay = float(model.predict(sample_encoded)[0])

    # SHAP computation
    shap_vals = explainer(sample_encoded).values[0]
    impacts = []
    for feat_name, impact in zip(expected_cols, shap_vals):
        if impact > 0:
            impacts.append(
                {"factor": feat_name, "impact_days": round(float(impact), 1)}
            )

    impacts = sorted(impacts, key=lambda x: x["impact_days"], reverse=True)[:3]
    total_imp = sum(x["impact_days"] for x in impacts) or 1.0
    for imp in impacts:
        imp["contribution_pct"] = round(
            (imp["impact_days"] / total_imp) * 100, 1
        )

    # Top bottleneck factor
    top_factor = impacts[0]["factor"] if impacts else "none"
    prescriptive_action = get_prescriptive_action(top_factor, plot)

    # Live GenAI 3-Step Mitigation Call
    ai_steps = generate_dynamic_mitigation_steps(
        khasra_no=plot["khasra_no"],
        project_name=plot["project"],
        delay_days=max(0, round(predicted_delay)),
        shap_drivers=impacts,
        fallback_action=prescriptive_action,
    )

    return {
        "plot_info": plot,
        "predicted_delay_days": max(0, round(predicted_delay)),
        "shap_breakdown": impacts,
        "prescriptive_recommendation": prescriptive_action,
        "ai_mitigation_steps": ai_steps,
    }


# Endpoint 4: "What-If" Counterfactual Simulator
class SimulationRequest(BaseModel):
    khasra_no: str
    simulated_disbursement_pct: float
    resolve_khata: bool
    resolve_forest: bool


@app.post("/api/simulate")
def simulate_mitigation(req: SimulationRequest):
    if req.khasra_no not in raw_plots:
        raise HTTPException(status_code=404, detail="Plot not found")

    plot = dict(raw_plots[req.khasra_no])

    # Apply simulated interventions
    plot["disbursement_pct"] = req.simulated_disbursement_pct
    if req.resolve_khata:
        plot["unpartitioned_khata"] = 0
    if req.resolve_forest:
        plot["forest_clearance"] = "Approved"

    # Inference with updated features
    sample_df = pd.DataFrame([plot])
    sample_encoded = pd.get_dummies(sample_df)
    for col in expected_cols:
        if col not in sample_encoded.columns:
            sample_encoded[col] = 0
    sample_encoded = sample_encoded[expected_cols]

    new_delay = float(model.predict(sample_encoded)[0])
    original_delay = raw_plots[req.khasra_no]["delay_days"]

    days_saved = max(0, original_delay - round(new_delay))

    return {
        "khasra_no": req.khasra_no,
        "original_delay_days": original_delay,
        "new_predicted_delay_days": max(0, round(new_delay)),
        "days_saved": days_saved,
        "risk_reduced": (
            "Yes"
            if new_delay < 45
            else "Moderate Reduction"
            if new_delay < 90
            else "Needs further action"
        ),
    }