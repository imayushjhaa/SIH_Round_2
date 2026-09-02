import pandas as pd
import numpy as np

def calculate_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes high-signal domain features for land risk prediction."""
    df = df.copy()
    
    # Financial Disparity Ratio
    df['comp_gap_ratio'] = np.where(
        df['comp_offered_lakhs'] > 0,
        (df['comp_demanded_lakhs'] - df['comp_offered_lakhs']) / df['comp_offered_lakhs'],
        0.0
    )
    
    # Litigation Density per 100 acres
    df['litigation_density'] = np.where(
        df['land_area_acres'] > 0,
        (df['litigation_cases'] / df['land_area_acres']) * 100,
        0.0
    )
    
    # Displacement Intensity (families per acre)
    df['displacement_intensity'] = np.where(
        df['land_area_acres'] > 0,
        df['affected_families'] / df['land_area_acres'],
        0.0
    )
    
    # Ordinal weight for forest clearance
    forest_weights = {'Approved': 0.0, 'Pending': 0.5, 'Rejected': 1.0}
    df['forest_clearance_weight'] = df['forest_clearance_status'].map(forest_weights).fillna(0.5)
    
    return df

def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """Handles missing values and type casting."""
    df['litigation_cases'] = df['litigation_cases'].fillna(0).astype(int)
    df['comp_offered_lakhs'] = df['comp_offered_lakhs'].fillna(0.0).astype(float)
    df['comp_demanded_lakhs'] = df['comp_demanded_lakhs'].fillna(0.0).astype(float)
    df['land_area_acres'] = df['land_area_acres'].fillna(1.0).astype(float)
    return df

def transform_single_project(payload: dict) -> dict:
    """Formats a single incoming API payload for ML inference."""
    df = pd.DataFrame([payload])
    df = clean_and_validate(df)
    df = calculate_derived_features(df)
    
    feature_cols = [
        'land_area_acres', 'affected_families', 'comp_offered_lakhs',
        'comp_demanded_lakhs', 'litigation_cases', 'comp_gap_ratio',
        'litigation_density', 'displacement_intensity', 'forest_clearance_weight'
    ]
    return df[feature_cols].iloc[0].to_dict()

if __name__ == "__main__":
    raw_df = pd.read_csv("Tushar_Work/mock_sample.csv")
    cleaned_df = clean_and_validate(raw_df)
    processed_df = calculate_derived_features(cleaned_df)
    print("\n--- Pipeline Success ---")
    print(processed_df[['project_id', 'comp_gap_ratio', 'litigation_density', 'displacement_intensity']].head())