#ifndef RISK_CALCULATOR_H
#define RISK_CALCULATOR_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Calculates the post-ML rule-adjusted risk score (0.0 to 100.0) based on
 * ground-level administrative parameters and litigation status.
 *
 * @param base_ml_score           Base risk score predicted by XGBoost / Tree model.
 * @param comp_offered            Compensation amount offered by authority (in Lakhs/Crores).
 * @param comp_demanded           Compensation amount demanded by land owner.
 * @param litigation_cases        Number of active court / legal disputes pending.
 * @param forest_clearance_status 0: Approved / Not Required, 1: Pending, 2: Rejected.
 * @return Adjusted risk score clamped strictly between 0.0 and 100.0.
 */
float calculate_adjusted_risk(
    float base_ml_score,
    float comp_offered,
    float comp_demanded,
    int litigation_cases,
    int forest_clearance_status
);

#ifdef __cplusplus
}
#endif

#endif // RISK_CALCULATOR_H
