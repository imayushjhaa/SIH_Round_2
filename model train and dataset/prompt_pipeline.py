# prompt_pipeline.py

CONTEXTUAL_ACTION_MAP = {
    "Litigation Cases": {
        "Highway": "Initiate Section 3H arbitration under NH Act 1956 via Competent Authority for Land Acquisition (CALA).",
        "Railway": "Convene Special Railway Land Acquisition Officer (RLAO) fast-track tribunal under Railways Act 1989.",
        "Default": "Fast-track LARR Authority tribunal hearings under Section 51 of RFCTLARR Act 2013."
    },
    "Forest Clearance": {
        "Highway": "Apply for linear infrastructure tree-felling relaxation on MoEFCC PARIVESH portal.",
        "Default": "Accelerate Stage-I compensatory afforestation (CA) land identification with State Forest Department."
    },
    "Env Clearance": {
        "Default": "Submit revised Environmental Impact Assessment (EIA) mitigation plan to SEIAA."
    },
    "Slao Officer Vacant": {
        "Default": "Depute an ad-hoc Additional District Collector to assume SLAO charge immediately."
    },
    "Title Dispute Count": {
        "Default": "Convene Gram Sabha dispute resolution camps and deposit disputed compensation into escrow."
    },
    "Comp Disbursal Delay Months": {
        "Default": "Deploy Direct Benefit Transfer (DBT) fast-track portal for verified titleholder payouts."
    },
    "Comp Gap Ratio": {
        "Highway": "Convene District Level Land Pricing Committee (DLLPC) ex-gratia approval under NHAI guidelines.",
        "Default": "Form a local negotiation panel to reconcile private demand with District Circle Rates."
    },
    "Public Objections Count": {
        "Default": "Conduct mandatory public hearing sessions to address local community grievances under SIA."
    }
}


def get_risk_tier(score: float) -> tuple[str, str]:
    """Classifies numerical score into risk category with color badge emoji."""
    if score <= 30.0:
        return "LOW RISK", "🟢"
    elif score <= 60.0:
        return "MEDIUM RISK", "🟡"
    else:
        return "HIGH RISK", "🔴"


def resolve_sector_action(feature_name: str, project_name: str) -> str:
    """Determines project sector from name and returns sector-aware statutory action."""
    p_lower = project_name.lower()
    if any(k in p_lower for k in ["highway", "expressway", "bypass"]):
        sector = "Highway"
    elif any(k in p_lower for k in ["rail", "freight"]):
        sector = "Railway"
    else:
        sector = "Default"

    for bottleneck, rules in CONTEXTUAL_ACTION_MAP.items():
        if bottleneck.lower() in feature_name.lower():
            return rules.get(sector, rules.get("Default", "Convene inter-departmental task force review."))
    
    return "Convene inter-departmental task force review to clear operational bottleneck."


def build_recommendation_prompt(project_name: str, risk_score: float, base_value: float, top_drivers: list) -> str:
    """Formats SHAP drivers into risk drivers requiring action vs protective factors maintained."""
    risk_level, emoji = get_risk_tier(risk_score)
    driver_lines = []
    
    for d in top_drivers:
        impact = d["shap_impact"]
        feature = d["feature"]
        val = d["feature_value"]
        
        if impact > 0:
            action = resolve_sector_action(feature, project_name)
            weeks_saved = round(impact * 0.4, 1)
            line = (
                f"• 🚨 RISK DRIVER: {feature} (Value: {val})\n"
                f"  - Risk Impact: +{impact} pts\n"
                f"  - Sector-Aware Action: {action}\n"
                f"  - Potential Score Reduction: -{impact} pts (Est. {weeks_saved} weeks saved)\n"
            )
        else:
            line = (
                f"• 🛡️ PROTECTIVE FACTOR: {feature} (Value: {val})\n"
                f"  - Risk Reduction: {impact} pts (Pulls risk below dataset average)\n"
                f"  - Status: Healthy / Favorable condition maintained.\n"
            )
        driver_lines.append(line)

    prompt = f"""
You are a Senior Regulatory & Land Acquisition Officer for infrastructure projects in India.
Analyze the following project risk evaluation and generate a concise executive summary for project officers. Do not write introductory fluff.

Project Name: {project_name}
Baseline Dataset Average Risk: {round(base_value, 1)}/100
Evaluated Risk Status: {emoji} {risk_level} ({risk_score}/100)

Top Risk Drivers, Sector-Aware Actions & Delay Reductions:
{"".join(driver_lines)}

Provide 3 bulleted executive action steps for immediate deployment:
"""
    return prompt.strip()