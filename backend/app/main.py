from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    # Temporarily switch directory so relative pickle loads resolve correctly
    cwd = os.getcwd()
    os.chdir(MODEL_DIR)
    
    from generate_dynamic import evaluate_project_dict
    ML_MODEL_LOADED = True
    print("ML Model loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load ML Pipeline ({e}).")
    ML_MODEL_LOADED = False
finally:
    os.chdir(cwd)  # Restore working directory

app = FastAPI(title="Land Acquisition Risk Assessment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# O(1) Lookup Cache for Mock Data
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


@app.get("/api/projects")
def get_all_projects():
    return MOCK_PROJECTS_LIST


@app.get("/api/projects/{project_id}")
def get_project_by_id(project_id: str):
    # Optimized O(1) dictionary lookup
    project = MOCK_PROJECTS_MAP.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/api/predict", response_model=ProjectResponse)
def predict_risk(data: ProjectInput):
    payload_dict = data.model_dump()

    # Pre-calculate common metrics
    comp_ratio = data.comp_demanded_lakhs / (data.comp_offered_lakhs + 1e-5)

    # 1. Spatial & Data Cleaner Operations
    if DATA_PIPELINE_LOADED:
        try:
            transform_single_project(payload_dict)
            calculate_regional_risk_density(
                target_lat=data.latitude,
                target_lng=data.longitude,
                all_projects=MOCK_PROJECTS_LIST
            )
        except Exception as err:
            print(f"Data Pipeline warning: {err}")

    # 2. ML Base Score Calculation
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

    # 3. C++ Scoring Engine Execution
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

    # Fallback score if C++ engine is offline or errors
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