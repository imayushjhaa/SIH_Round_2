from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectInput(BaseModel):
    project_name: str = Field(..., example="NH-66 Expansion")
    district: str = Field(..., example="Raigad")
    state: str = Field(..., example="Maharashtra")
    latitude: float = Field(..., example=18.5158)
    longitude: float = Field(..., example=73.1812)
    land_area_acres: float = Field(..., example=120.5)
    affected_families: int = Field(..., example=450)
    comp_offered_lakhs: float = Field(..., example=1200.0)
    comp_demanded_lakhs: float = Field(..., example=1800.0)
    litigation_cases: int = Field(..., example=4)
    forest_clearance_status: str = Field(..., example="Pending")
    stage: str = Field(..., example="Compensation Disbursal")

class RiskFactor(BaseModel):
    factor: str
    contribution: float

class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    location: dict
    risk_score: int
    risk_level: str
    top_risk_factors: List[RiskFactor]
    recommended_actions: List[str]