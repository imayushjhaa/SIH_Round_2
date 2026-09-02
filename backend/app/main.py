from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import ProjectInput, ProjectResponse
import random
import sys
import os

# Add parent directory to path so we can import cpp_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from cpp_engine.test_bridge import run_cpp_risk_engine
    CPP_ENGINE_LOADED = True
except Exception as e:
    print(f"Warning: Could not load C++ engine ({e}). Falling back to pure Python logic.")
    CPP_ENGINE_LOADED = False

app = FastAPI(
    title="Land Acquisition Risk Assessment API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_PROJECTS = [
    {
        "project_id": "PRJ_101",
        "project_name": "NH-66 Expansion",
        "location": {"district": "Raigad", "state": "Maharashtra", "lat": 18.5158, "lng": 73.1812},
        "risk_score": 82,
        "risk_level": "High",
        "top_risk_factors": [
            {"factor": "Compensation Gap Ratio", "contribution": 38.5},
            {"factor": "Pending Litigation Cases", "contribution": 28.2},
            {"factor": "Forest Clearance Status", "contribution": 15.3}
        ],
        "recommended_actions": [
            "Initiate SLAO fast-track tribunal negotiations.",
            "Form expert committee to recalculate DBT rates."
        ]
    }
]

@app.get("/")
def health_check():
    return {"status": "online", "message": "Backend API is running!"}

@app.get("/api/projects")
def get_all_projects():
    return MOCK_PROJECTS

@app.get("/api/projects/{project_id}")
def get_project_by_id(project_id: str):
    for project in MOCK_PROJECTS:
        if project["project_id"] == project_id:
            return project
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/api/predict", response_model=ProjectResponse)
def predict_risk(data: ProjectInput):
    # Convert string clearance status to int code expected by C++
    clearance_map = {"Approved": 0, "Pending": 1, "Rejected": 2}
    clearance_code = clearance_map.get(data.forest_clearance_status, 1)

    # Temporary baseline ML probability (Will be replaced by Person 5's ML model)
    base_ml_score = 45.0  

    # Call Person 2's C++ Engine if loaded, otherwise fallback to Python
    if CPP_ENGINE_LOADED:
        calc_score = int(run_cpp_risk_engine(
            ml_score=base_ml_score,
            offered=data.comp_offered_lakhs,
            demanded=data.comp_demanded_lakhs,
            litigations=data.litigation_cases,
            clearance_code=clearance_code
        ))
    else:
        comp_ratio = data.comp_demanded_lakhs / (data.comp_offered_lakhs + 1e-5)
        calc_score = min(100, int((comp_ratio * 20) + (data.litigation_cases * 10)))

    level = "High" if calc_score > 70 else ("Medium" if calc_score > 40 else "Low")

    comp_ratio = data.comp_demanded_lakhs / (data.comp_offered_lakhs + 1e-5)

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
        "risk_level": level,
        "top_risk_factors": [
            {"factor": "Compensation Gap", "contribution": round(comp_ratio * 15, 1)},
            {"factor": "Litigation Cases", "contribution": float(data.litigation_cases * 8)}
        ],
        "recommended_actions": [
            "Fast-track tribunal hearings.",
            "Review environment clearance delays."
        ]
    }