#include "risk_calculator.h"
#include <algorithm>

extern "C" {

float calculate_adjusted_risk(
    float base_ml_score,
    float comp_offered,
    float comp_demanded,
    int litigation_cases,
    int forest_clearance_status
) {
    float score = base_ml_score;

    // Rule 1: Compensation Disparity Multiplier
    if (comp_offered > 0.0f) {
        float gap_ratio = (comp_demanded - comp_offered) / comp_offered;
        if (gap_ratio > 0.25f) {
            score += (gap_ratio * 15.0f); // Penalize large compensation gaps
        }
    }

    // Rule 2: Litigation Weighting
    score += (litigation_cases * 4.5f);

    // Rule 3: Environmental Clearance Status Impact
    if (forest_clearance_status == 1) {      // Pending
        score += 8.0f;
    } else if (forest_clearance_status == 2) { // Rejected
        score += 25.0f;
    }

    // Clamp final score strictly between 0.0 and 100.0
    if (score > 100.0f) score = 100.0f;
    if (score < 0.0f) score = 0.0f;

    return score;
}

}