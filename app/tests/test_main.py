from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_generate_route():
    body = {
        "start": "Hauptbahnhof Leipzig",
        "ziel": "Völkerschlachtdenkmal Leipzig",
        "entfernung": 2.5,
        "optionen": "",
        "rundreise": False,
        "mode": "walk"
    }
    response = client.post("/api/generate-route", json=body)
    assert response.status_code == 200
    data = response.json()

    assert "geojson" in data
    assert "waypoints" in data

    geojson = data["geojson"]

    for key in ["features", "properties", "type"]:
        assert key in geojson
    assert geojson["type"] == "FeatureCollection"

    features = geojson["features"]
    assert len(features) > 0
    feature = features[0]
    for key in ["type", "properties", "geometry"]:
        assert key in feature
    assert feature["type"] == "Feature"

    props = feature["properties"]
    for key in ["mode", "waypoints", "units", "distance", "distance_units", "time", "legs"]:
        assert key in props

    for wp in props["waypoints"]:
        assert "location" in wp
        assert "original_index" in wp

    legs = props["legs"]
    assert isinstance(legs, list)
    for leg in legs:
        assert "distance" in leg
        assert "time" in leg
        assert "steps" in leg

    geometry = feature["geometry"]
    for key in ["type", "coordinates"]:
        assert key in geometry
    assert geometry["type"] == "MultiLineString"

    waypoints = data["waypoints"]
    assert all(isinstance(wp, str) for wp in waypoints)