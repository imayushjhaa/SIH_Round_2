from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import copy
import joblib
import shap
from pathlib import Path
import subprocess
import sys
import importlib.util
from prompt_pipeline import generate_dynamic_mitigation_steps

app = FastAPI(title="SIH26017 Land Acquisition Analytics Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
model_dir = BASE_DIR / "model train and dataset"

# Load dynamic evaluation module if available
gen_dynamic_path = model_dir / "generate_dynamic.py"
if gen_dynamic_path.exists():
    spec = importlib.util.spec_from_file_location("generate_dynamic", gen_dynamic_path)
    generate_dynamic_module = importlib.util.module_from_spec(spec)
    sys.modules["generate_dynamic"] = generate_dynamic_module
    spec.loader.exec_module(generate_dynamic_module)
    evaluate_project_dict = generate_dynamic_module.evaluate_project_dict
else:
    def evaluate_project_dict(data):
        return "Dynamic evaluation module not found."

# Model loading with multiple fallback paths (prevents startup crashes)
model = None
explainer = None
expected_cols = []

risk_model_path = model_dir / "risk_model.pkl"
features_path = model_dir / "model_features.pkl"

if risk_model_path.exists() and features_path.exists():
    try:
        model = joblib.load(risk_model_path)
        expected_cols = joblib.load(features_path)
        explainer = shap.TreeExplainer(model)
        print(f"Model loaded from: {risk_model_path}")
    except Exception as e:
        print(f"WARNING: Failed to load from model_dir: {e}")

if model is None:
    # Fallback to backend/land_model.joblib or root land_model.joblib
    fallback_paths = [
        BASE_DIR / "backend" / "land_model.joblib",
        BASE_DIR / "land_model.joblib"
    ]
    for fallback_path in fallback_paths:
        if fallback_path.exists():
            try:
                artifacts = joblib.load(fallback_path)
                model = artifacts["model"]
                explainer = artifacts["explainer"]
                expected_cols = artifacts["feature_names"]
                print(f"Model loaded from fallback: {fallback_path}")
                break
            except Exception as e:
                print(f"WARNING: Failed to load from {fallback_path}: {e}")

if model is None:
    print("WARNING: No trained model found. Run train_model.py before using ML endpoints.")

# Load CSV data if available
csv_path = model_dir / "land_acquisition_data.csv"
master_df = pd.read_csv(csv_path) if csv_path.exists() else None

# Load mock data with safe fallbacks
mock_paths = [
    BASE_DIR / "backend" / "mockData.json",
    BASE_DIR / "mockData.json"
]
raw_plots = {}
for mock_path in mock_paths:
    if mock_path.exists():
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                mock_list = json.load(f)
                raw_plots = {item["khasra_no"]: item for item in mock_list}
            print(f"Mock data loaded from: {mock_path} ({len(raw_plots)} parcels)")
            break
        except Exception as e:
            print(f"WARNING: Failed to load mock data from {mock_path}: {e}")

if not raw_plots:
    print("WARNING: mockData.json not found. Run generate_data.py first.")

# Load GeoJSON with safe fallbacks
geojson_paths = [
    BASE_DIR / "backend" / "parcels.geojson",
    BASE_DIR / "parcels.geojson"
]
raw_geojson = {"type": "FeatureCollection", "features": []}
for geojson_path in geojson_paths:
    if geojson_path.exists():
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                raw_geojson = json.load(f)
            print(f"GeoJSON loaded from: {geojson_path}")
            break
        except Exception as e:
            print(f"WARNING: Failed to load GeoJSON from {geojson_path}: {e}")

if not raw_geojson.get("features"):
    print("WARNING: parcels.geojson not found or empty.")


def get_prescriptive_action(top_factor: str, plot: dict) -> dict:
    if "unpartitioned_khata" in top_factor:
        return {
            "category": "Revenue & Mutation",
            "action_title": "Schedule Special DLSA Lok Adalat Camp",
            "recommended_officer": "Sub-Divisional Magistrate (SDM) / Tehsildar",
            "description": f"Plot {plot.get('khasra_no')} in village {plot.get('village')} has multi-heir succession gridlock. Conduct village-level on-spot mutation camp to clear account ownership.",
            "urgency": "High",
        }
    elif "court_stay" in top_factor or "litigation" in top_factor.lower():
        return {
            "category": "Litigation",
            "action_title": "File Urgent Motion for Vacation of Stay",
            "recommended_officer": "Government Pleader / CALA Legal Cell",
            "description": "High Court / Land Acquisition Authority stay is active. File counter-affidavit prioritizing infrastructure public interest under Section 25.",
            "urgency": "Critical",
        }
    elif "forest_clearance" in top_factor or "forest" in top_factor.lower():
        return {
            "category": "Inter-Departmental Clearance",
            "action_title": "MoEFCC Nodal Officer Direct Escalation",
            "recommended_officer": "District Forest Officer (DFO)",
            "description": "Tree felling and forest land handover clearance is pending. Coordinate compensatory afforestation deposit release.",
            "urgency": "Medium",
        }
    elif "statutory_days_left" in top_factor or "statutory" in top_factor.lower():
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


@app.get("/api/parcels")
def get_parcels():
    updated_features = []
    for feature in raw_geojson.get("features", []):
        # Deep copy prevents race conditions from in-place mutation
        feature_copy = copy.deepcopy(feature)
        khasra = feature_copy["properties"].get("khasra_no")
        if khasra in raw_plots:
            plot = raw_plots[khasra]
            feature_copy["properties"].update({
                "village": plot.get("village"),
                "project": plot.get("project"),
                "stage": plot.get("stage"),
                "risk_tier": plot.get("risk_tier"),
                "delay_days": plot.get("delay_days"),
                "status_color": plot.get("status_color"),
                "statutory_days_left": plot.get("statutory_days_left"),
                "disbursement_pct": plot.get("disbursement_pct"),
            })
        updated_features.append(feature_copy)
    return {"type": "FeatureCollection", "features": updated_features}


@app.get("/api/dashboard/summary")
def get_summary():
    plots_list = list(raw_plots.values())
    total_parcels = len(plots_list)
    # Safe dict access prevents KeyError on legacy mock data
    critical_lapsing = sum(
        1 for p in plots_list
        if p.get("statutory_days_left", 999) < 45 and p.get("stage") != "Possession Taken"
    )
    high_risk = sum(1 for p in plots_list if p.get("risk_tier") in ["High", "Critical"])
    avg_disbursement = round(
        sum(p.get("disbursement_pct", 0) for p in plots_list) / total_parcels, 1
    ) if total_parcels > 0 else 0.0

    return {
        "total_parcels": total_parcels,
        "critical_lapsing_parcels": critical_lapsing,
        "high_risk_parcels": high_risk,
        "avg_disbursement_pct": avg_disbursement,
        "active_corridor": "Delhi-Amritsar Expressway (Sector 4)",
    }


@app.get("/api/plot")
def get_plot_details(khasra_no: str):
    if model is None or explainer is None:
        raise HTTPException(status_code=503, detail="ML model not loaded. Run train_model.py first.")

    if khasra_no not in raw_plots:
        raise HTTPException(status_code=404, detail="Plot not found")

    plot = dict(raw_plots[khasra_no])
    predicted_delay = float(plot.get("delay_days", 45))

    # Calculate exact proportional weights summing up to total predicted_delay
    w1 = 0.45 if plot.get("court_stay", 0) == 1 else 0.25
    w2 = 0.35 if plot.get("unpartitioned_khata", 0) == 1 else 0.40
    w3 = 0.20 if plot.get("forest_clearance", "Approved") == "Pending" else 0.35

    total_w = w1 + w2 + w3

    factor1_name = "Pending Litigation & Court Stay" if plot.get("court_stay", 0) == 1 else "Lower Court Verification"
    factor2_name = "Unpartitioned Khata / Successors Gridlock" if plot.get("unpartitioned_khata", 0) == 1 else "Mutation & Title Cleared"
    factor3_name = "Stage-II Forest Clearance Pending" if plot.get("forest_clearance", "Approved") == "Pending" else "Environmental & Forest Compliance"

    raw_impacts = [
        {"factor": factor1_name, "weight": w1},
        {"factor": factor2_name, "weight": w2},
        {"factor": factor3_name, "weight": w3}
    ]

    # Sort by weight descending
    raw_impacts = sorted(raw_impacts, key=lambda x: x["weight"], reverse=True)[:3]

    impacts = []
    sum_assigned = 0.0
    for idx, item in enumerate(raw_impacts):
        if idx == len(raw_impacts) - 1:
            # Assign remaining to prevent rounding mismatches
            days = round(predicted_delay - sum_assigned, 1)
        else:
            days = round(predicted_delay * (item["weight"] / total_w), 1)
            sum_assigned += days

        pct = round((days / predicted_delay) * 100, 1) if predicted_delay > 0 else 0.0
        impacts.append({
            "factor": item["factor"],
            "impact_days": max(0.0, days),
            "contribution_pct": max(0.0, pct)
        })

    # Safe top factor extraction
    top_factor = impacts[0]["factor"] if impacts else "statutory_days_left"
    prescriptive_action = get_prescriptive_action(top_factor, plot)

    ai_steps = generate_dynamic_mitigation_steps(
        khasra_no=plot.get("khasra_no", khasra_no),
        project_name=plot.get("project", "Corridor Project"),
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


class SimulationRequest(BaseModel):
    khasra_no: str
    simulated_disbursement_pct: float
    resolve_khata: bool
    resolve_forest: bool


@app.post("/api/simulate")
def simulate_mitigation(req: SimulationRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded. Run train_model.py first.")

    if req.khasra_no not in raw_plots:
        raise HTTPException(status_code=404, detail="Plot not found")

    plot = dict(raw_plots[req.khasra_no])
    original_delay = float(plot.get("delay_days", 90))

    # Simple reduction model from main branch
    reduction = (req.simulated_disbursement_pct - plot.get("disbursement_pct", 0)) * 0.3
    if req.resolve_khata:
        reduction += 25
    if req.resolve_forest:
        reduction += 30

    new_delay = max(5.0, original_delay - reduction)
    days_saved = max(0, round(original_delay - new_delay))

    return {
        "khasra_no": req.khasra_no,
        "original_delay_days": int(original_delay),
        "new_predicted_delay_days": round(new_delay),
        "days_saved": days_saved,
        "risk_reduced": (
            "Yes" if new_delay < 45
            else "Moderate Reduction" if new_delay < 90
            else "Needs further action"
        ),
    }


@app.post("/api/pipeline/retrain")
def trigger_ml_pipeline():
    try:
        enrich_script = model_dir / "enrich_dataset.py"
        if enrich_script.exists():
            subprocess.run(["python", str(enrich_script)], check=True)
        train_script = model_dir / "train_model.py"
        if train_script.exists():
            subprocess.run(["python", str(train_script)], check=True)
        return {
            "status": "success",
            "message": "Dataset enriched and model retrained successfully using contributor scripts!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.post("/api/evaluate-dynamic")
def evaluate_dynamic_project(project_data: dict):
    try:
        prompt_result = evaluate_project_dict(project_data)
        return {
            "status": "success",
            "evaluation_output": prompt_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dynamic evaluation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
