import numpy as np

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates spherical distance between two coordinates in kilometers."""
    R = 6371.0  # Earth radius in KM
    
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = (np.sin(delta_phi / 2.0) ** 2 +
         np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return float(R * c)

def find_nearby_projects(target_lat: float, target_lng: float, projects: list, radius_km: float = 50.0) -> list:
    """Filters projects within radius_km and sorts by nearest distance."""
    nearby = []
    for p in projects:
        dist = haversine_distance(target_lat, target_lng, p['latitude'], p['longitude'])
        if dist <= radius_km:
            p_copy = p.copy()
            p_copy['distance_km'] = round(dist, 2)
            nearby.append(p_copy)
    return sorted(nearby, key=lambda x: x['distance_km'])

def calculate_regional_risk_density(target_lat: float, target_lng: float, all_projects: list, radius_km: float = 75.0) -> dict:
    """
    Computes regional cluster risk:
    - How many projects exist within radius?
    - How many pending litigation cases exist in this immediate cluster?
    """
    nearby = find_nearby_projects(target_lat, target_lng, all_projects, radius_km)
    
    total_nearby = len(nearby)
    total_litigation = sum(p.get('litigation_cases', 0) for p in nearby)
    
    cluster_score = min(100.0, (total_litigation * 10) + (total_nearby * 5))
    
    return {
        "nearby_projects_count": total_nearby,
        "cluster_litigation_cases": total_litigation,
        "regional_dispute_score": round(cluster_score, 2),
        "nearby_list": nearby
    }

if __name__ == "__main__":
    sample_projects = [
        {"project_id": "PRJ_101", "latitude": 18.5158, "longitude": 73.1812, "litigation_cases": 4},
        {"project_id": "PRJ_102", "latitude": 19.2183, "longitude": 72.9781, "litigation_cases": 1},
        {"project_id": "PRJ_103", "latitude": 18.9000, "longitude": 73.1000, "litigation_cases": 6}
    ]
    
    res = calculate_regional_risk_density(18.5158, 73.1812, sample_projects, radius_km=60.0)
    print("--- Spatial Cluster Test ---")
    print(f"Projects found nearby: {res['nearby_projects_count']}")
    print(f"Regional Dispute Score: {res['regional_dispute_score']}")