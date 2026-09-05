import os

# Dynamic In-Memory Synthesizer (Instant 0ms Latency & Statutorily Accurate Per Parcel)
def generate_dynamic_mitigation_steps(
    khasra_no: str, 
    project_name: str, 
    delay_days: int, 
    shap_drivers: list, 
    fallback_action: dict
) -> list:
    """
    Synthesizes parcel-specific, mathematically tailored statutory directives instantly
    without external API latency blocking the UI.
    """
    category = fallback_action.get("category", "")
    
    # 0. Statutory Hard Guardrail: Lapsed Proceedings under RFCTLARR Sec 19(7)
    if "Statutory Abatement" in category:
        return [
            f"De-Novo Section 11 Notification: Direct Competent Authority (CALA) to issue fresh preliminary notification for {khasra_no} following statutory abatement.",
            "Re-conduct Social Impact Assessment (SIA): Request expeditious waiver/fast-track SIA update from State Revenue Department citing infrastructure continuity.",
            "Alignment Priority Freeze: Direct Project Director ({project_name}) to maintain freeze on contiguous stretch alignment to avoid corridor redesign."
        ]

    if not shap_drivers:
        return [
            f"Statutory Notice for {khasra_no}: Issue Section 37 award declaration.",
            "PFMS Clearance: Direct CALA account wing to disburse compensation.",
            "Possession Handover: Deploy Kanungo team for physical corridor peg-marking."
        ]

    top = shap_drivers[0]
    factor = top.get("factor", "").lower()
    impact = top.get("impact_days", 0)
    pct = top.get("contribution_pct", 0)

    steps = []

    # 1. Litigation & Court Stay Bottlenecks
    if "court_stay" in factor or "litigation" in factor:
        steps.append(
            f"Vacate Stay for {khasra_no} (Contributing +{impact}d / {pct}%): Direct District Attorney & CALA Legal Cell to file urgent Interlocutory Application under Section 20A of Specific Relief Act."
        )
        steps.append(
            f"Section 77(2) Escrow Deposit: Deposit contested compensation for {khasra_no} directly with the LARA Authority to enable Section 38 possession without awaiting suit disposal."
        )
        steps.append(
            f"High Court Infrastructure Bench: CALA to pray for day-to-day expedited hearing citing the {delay_days}-day projected corridor disruption."
        )

    # 2. Succession & Khata Partition Bottlenecks
    elif "khata" in factor or "unpartitioned" in factor:
        steps.append(
            f"14-Day Summary Partition Drive ({khasra_no}): Direct Tehsildar to launch village-level camp to issue provisional apportionment orders for all co-sharers (Resolves +{impact}d delay)."
        )
        steps.append(
            "Indemnity Bond Payouts: Authorize CALA to release undisputed inheritance shares against registered indemnity bonds under State Land Acquisition Rules."
        )
        steps.append(
            "DLSA Lok Adalat Conciliation: Schedule urgent pre-litigation settlement bench to resolve family succession gridlock on-spot."
        )

    # 3. Forest & Environmental Clearances
    elif "forest" in factor:
        steps.append(
            f"PARIVESH Portal Stage-II Expedite: Direct DFO and Project Director to upload compliance certificate within 7 days (Mitigates +{impact}d risk)."
        )
        steps.append(
            "CAMPA Fund Transfer: Authorize instant online DBT transfer of Net Present Value (NPV) & Compensatory Afforestation charges."
        )
        steps.append(
            "Section 2 Working Permission: Request Principal Chief Conservator of Forests (PCCF) for provisional right-of-way access."
        )

    # 4. Statutory Lapsing Watchdog (Section 19(7))
    elif "statutory" in factor or delay_days > 250 or "Statutory Compliance" in category:
        steps.append(
            f"Emergency Section 19 Gazette Publication: Direct District Magistrate (DM) to sign final declaration for {khasra_no} within 48h to prevent statutory lapse under Section 19(7)."
        )
        steps.append(
            "72-Hour Boundary Demarcation: Deploy dedicated Kanungo and Revenue Task Force to freeze contiguous alignment boundaries."
        )
        steps.append(
            "State Press Priority Dispatch: Transmit e-Gazette notification directly to the Government Printing Press under executive priority."
        )

    # 5. Compensation & Disbursement Gaps
    else:
        steps.append(
            f"PFMS Bulk DBT Drive for {khasra_no}: CALA accounts unit to disburse pending award amount to clear the +{impact}d financial roadblock."
        )
        steps.append(
            "Special Banking Redressal Camp: Set up bank account verification desk at Panchayat Bhavan for instant validation."
        )
        steps.append(
            "Section 38 Formal Notice: Issue mandatory 60-day physical possession notice to land occupants upon clearing 80% award threshold."
        )

    return steps