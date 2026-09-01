import json

with open("mockData.json", "r") as f:
    mock_plots = json.load(f)

# Real agricultural farmland coordinates (Haryana border greenfield stretch)
base_lat = 28.7520
base_lng = 76.9150

features = []
grid_cols = 5

for idx, plot in enumerate(mock_plots[:25]):
    row = idx // grid_cols
    col = idx % grid_cols

    # Agricultural plot dimensions (rectangular farmland strip)
    w = 0.0016
    h = 0.0011

    min_lng = base_lng + (col * w)
    max_lng = min_lng + (w * 0.92)
    min_lat = base_lat + (row * h)
    max_lat = min_lat + (h * 0.90)

    polygon_coords = [
        [
            [round(min_lng, 6), round(min_lat, 6)],
            [round(max_lng, 6), round(min_lat, 6)],
            [round(max_lng, 6), round(max_lat, 6)],
            [round(min_lng, 6), round(max_lat, 6)],
            [round(min_lng, 6), round(min_lat, 6)],
        ]
    ]

    feature = {
        "type": "Feature",
        "id": plot["khasra_no"],
        "properties": {
            "khasra_no": plot["khasra_no"],
            "village": plot["village"],
            "project": plot["project"],
            "stage": plot["stage"],
            "risk_tier": plot["risk_tier"],
            "delay_days": plot["delay_days"],
            "status_color": plot["status_color"],
            "statutory_days_left": plot["statutory_days_left"],
            "disbursement_pct": plot["disbursement_pct"],
        },
        "geometry": {"type": "Polygon", "coordinates": polygon_coords},
    }
    features.append(feature)

geojson_data = {"type": "FeatureCollection", "features": features}

with open("parcels.geojson", "w") as f:
    json.dump(geojson_data, f, indent=2)

print("Updated parcels.geojson with agricultural farmland coordinates!")