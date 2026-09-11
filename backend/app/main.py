from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models import ProjectInput, ProjectResponse
import random
import sys
import os

# Path routing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Module Loading with Guard Flags
try:
    from cpp_engine.test_bridge import run_cpp_risk_engine
    CPP_ENGINE_LOADED = True
except Exception as e:
    print(f"Warning: Could not load C++ engine ({e}).")
    CPP_ENGINE_LOADED = False

# Data Pipeline Loading
try:
    from Data_Pipeline.data_cleaner import transform_single_project
    from Data_Pipeline.spatial_algo import calculate_regional_risk_density
    DATA_PIPELINE_LOADED = True
except Exception as e:
    print(f"Warning: Could not load Data Pipeline ({e}).")
    DATA_PIPELINE_LOADED = False

# ML Model Loading
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../model train and dataset"))
if MODEL_DIR in sys.path:
    sys.path.remove(MODEL_DIR)
sys.path.insert(0, MODEL_DIR)

# ML Model Pipeline
try:
    cwd = os.getcwd()
    os.chdir(MODEL_DIR)
    from generate_dynamic import evaluate_project_dict
    ML_MODEL_LOADED = True
    print("ML Model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load ML Pipeline ({e}).")
    ML_MODEL_LOADED = False
finally:
    os.chdir(cwd)

app = FastAPI(title="Land Acquisition Risk Assessment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model for What-If Simulation Payload
class SimulationInput(BaseModel):
    khasra_no: str
    simulated_disbursement_pct: float
    resolve_khata: bool
    resolve_forest: bool

# O(1) Lookup Cache for Mock Data & Plot Info
MOCK_PROJECTS_LIST = [
    {
        "project_id": "PRJ_101",
        "project_name": "NH-66 Expansion",
        "district": "Raigad",
        "state": "Maharashtra",
        "latitude": 18.5158,
        "longitude": 73.1812,
        "location": {"district": "Raigad", "state": "Maharashtra", "lat": 18.5158, "lng": 73.1812},
        "risk_score": 82,
        "risk_level": "High",
        "top_risk_factors": [
            {"factor": "Compensation Gap Ratio", "contribution": 38.5},
            {"factor": "Pending Litigation Cases", "contribution": 28.2}
        ],
        "recommended_actions": ["Fast-track tribunal negotiations."]
    }
]
MOCK_PROJECTS_MAP = {p["project_id"]: p for p in MOCK_PROJECTS_LIST}

CLEARANCE_MAP = {"Approved": 0, "Pending": 1, "Rejected": 2}


@app.get("/")
def health_check():
    return {"status": "online", "message": "Backend API is running!"}


@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    return {
        "active_corridor": "Delhi-Amritsar Expressway (Sector 4)",
        "total_parcels": 30,
        "critical_lapsing_parcels": 11,
        "high_risk_parcels": 13,
        "safe_parcels": 6,
        "avg_disbursement_pct": 46.2
    }


@app.get("/api/projects")
def get_all_projects():
    return MOCK_PROJECTS_LIST


@app.get("/api/plot/{khasra_no:path}")
def get_plot_by_khasra(khasra_no: str):
    # Generate deterministic pseudo-unique values based on khasra string so every plot differs
    seed_val = sum(ord(c) for c in khasra_no)
    random.seed(seed_val)
    
    dynamic_delay = 45 + (seed_val % 95)  # Varies between 45 to 140 days
    disbursement = 30 + (seed_val % 55)   # Varies between 30% to 85%
    days_left = 20 + (seed_val % 100) - 40 # Can be critical or safe
    
    risk_tier = "Critical" if dynamic_delay > 110 else ("High" if dynamic_delay > 80 else "Moderate")
    
    return {
        "plot_info": {
            "khasra_no": khasra_no,
            "village": "Rohad",
            "project": "KMP Expressway (Asaudha Stretch)",
            "stage": "Section 15 (Hearing)" if days_left > 0 else "Section 11 (Notice)",
            "statutory_days_left": days_left,
            "sec_11_date": "2025-10-15",
            "risk_tier": risk_tier,
            "disbursement_pct": disbursement,
            "unpartitioned_khata": seed_val % 2
        },
        "predicted_delay_days": dynamic_delay,
        "shap_breakdown": [
            {"factor": "Compensation Gap Ratio", "impact_days": round(dynamic_delay * 0.4, 1), "contribution_pct": 45.0},
            {"factor": "Pending Litigation Cases", "impact_days": round(dynamic_delay * 0.3, 1), "contribution_pct": 30.0},
            {"factor": "Forest Clearance Delay", "impact_days": round(dynamic_delay * 0.3, 1), "contribution_pct": 25.0}
        ],
        "prescriptive_recommendation": {
            "action_title": "Expedite Stage-II Forest Clearance" if seed_val % 2 == 0 else "Fast-Track Tribunal Negotiations",
            "description": "Request Principal Chief Conservator of Forests (PCCF) for provisional right-of-way access.",
            "recommended_officer": "District Forest Officer (DFO)"
        },
        "ai_mitigation_steps": [
            "CAMPA Fund Transfer: Authorize instant DBT transfer of Net Present Value (NPV) & Compensatory Afforestation charges.",
            "Section 2K Working Permission: Request Principal Chief Conservator of Forests (PCCF) for provisional right-of-way access."
        ]
    }


@app.post("/api/simulate")
def run_what_if_simulation(data: SimulationInput):
    # Dynamic calculation based on frontend slider and checkbox values
    base_delay = 126
    disbursement_reduction = int(data.simulated_disbursement_pct * 0.6)
    khata_reduction = 25 if data.resolve_khata else 0
    forest_reduction = 30 if data.resolve_forest else 0
    
    total_saved = disbursement_reduction + khata_reduction + forest_reduction
    new_delay = max(12, base_delay - total_saved)
    
    return {
        "khasra_no": data.khasra_no,
        "new_predicted_delay_days": new_delay,
        "days_saved": total_saved,
        "status": "success"
    }


@app.post("/api/predict", response_model=ProjectResponse)
def predict_risk(data: ProjectInput):
    payload_dict = data.model_dump()
    comp_ratio = data.comp_demanded_lakhs / (data.comp_offered_lakhs + 1e-5)

    base_ml_score = 45.0
    if ML_MODEL_LOADED:
        try:
            ml_result = evaluate_project_dict(payload_dict)
            if isinstance(ml_result, dict):
                base_ml_score = float(ml_result.get("risk_score", 45.0))
            elif isinstance(ml_result, (int, float)):
                base_ml_score = float(ml_result)
        except Exception as err:
            print(f"ML Model evaluation warning: {err}")

    calc_score = None
    if CPP_ENGINE_LOADED:
        try:
            clearance_code = CLEARANCE_MAP.get(data.forest_clearance_status, 1)
            calc_score = int(run_cpp_risk_engine(
                ml_score=base_ml_score,
                offered=data.comp_offered_lakhs,
                demanded=data.comp_demanded_lakhs,
                litigations=data.litigation_cases,
                clearance_code=clearance_code
            ))
        except Exception as err:
            print(f"C++ Engine warning: {err}")

    if calc_score is None:
        calc_score = min(100, int((comp_ratio * 20) + (data.litigation_cases * 10)))

    risk_level = "High" if calc_score > 70 else ("Medium" if calc_score > 40 else "Low")

    return {
        "project_id": f"PRJ_{random.randint(100, 999)}",
        "project_name": data.project_name,
        "location": {
            "district": data.district,
            "state": data.state,
            "lat": data.latitude,
            "lng": data.longitude
        },
        "risk_score": calc_score,
        "risk_level": risk_level,
        "top_risk_factors": [
            {"factor": "Compensation Gap", "contribution": round(comp_ratio * 15, 1)},
            {"factor": "Litigation Cases", "contribution": float(data.litigation_cases * 8)}
        ],
        "recommended_actions": [
            "Fast-track tribunal hearings.",
            "Review environment clearance delays."
        ]
    }