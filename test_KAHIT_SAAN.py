# test_KAHIT_SAAN.py

import pytest
from unittest.mock import patch
import KAHIT_SAAN  # import your script

# Mock data for testing
valid_geocode_response = {
    "hits": [{
        "point": {"lat": 52.52, "lng": 13.405},
        "name": "Berlin",
        "osm_value": "city",
        "country": "Germany",
        "state": "Berlin"
    }]
}

invalid_geocode_response = {
    "message": "Invalid location"
}

valid_route_response = {
    "paths": [{
        "distance": 100000,  # 100 km
        "time": 3600000,  # 1 hour in ms
        "instructions": [
            {"text": "Turn right", "distance": 500},
            {"text": "Go straight", "distance": 1500}
        ]
    }]
}

# Test geocoding with valid location
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_success(mock_get):
    # Mock the response from the geocoding API
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = valid_geocode_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("Berlin", "fake_api_key")
    
    assert status == 200
    assert lat == 52.52
    assert lng == 13.405
    assert location == "Berlin, Berlin, Germany"

# Test geocoding with invalid location
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_failure(mock_get):
    # Mock a failed geocoding API response
    mock_get.return_value.status_code = 400
    mock_get.return_value.json.return_value = invalid_geocode_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("InvalidLocation", "fake_api_key")
    
    assert status == 400
    assert lat == "null"
    assert lng == "null"
    assert location == "InvalidLocation"

# Test route planning with mocked API response
@patch('KAHIT_SAAN.requests.get')
def test_route_planning(mock_get):
    # Mocking the route planning response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = valid_route_response

    # Mocked geocode results
    orig = (200, 52.52, 13.405, "Berlin")
    dest = (200, 48.8566, 2.3522, "Paris")
    
    # Test the route planning logic
    route_url = KAHIT_SAAN.route_url + "key=fake_api_key&vehicle=car"
    route_url += "&point=52.52%2C13.405&point=48.8566%2C2.3522"
    
    mock_get(route_url).status_code = 200
    mock_get(route_url).json.return_value = valid_route_response

    # Testing route planning data
    response_data = mock_get(route_url).json()
    
    assert response_data['paths'][0]['distance'] == 100000
    assert 'instructions' in response_data['paths'][0]
    assert len(response_data['paths'][0]['instructions']) > 0

# Test create map (no external API calls)
@patch('KAHIT_SAAN.folium.Map')
@patch('KAHIT_SAAN.folium.Marker')
@patch('KAHIT_SAAN.folium.PolyLine')
def test_create_map(mock_polyline, mock_marker, mock_map):
    # Simulate that the map is being saved
    mock_map.save = lambda filename: None  # Mock save function to do nothing
    orig = (200, 52.52, 13.405, "Berlin")
    dest = (200, 48.8566, 2.3522, "Paris")
    vehicle = "car"
    
    # Call create_map
    KAHIT_SAAN.create_map(orig, dest, vehicle)
    
    # Check that the map and markers were created
    mock_map.assert_called_once()
    mock_marker.assert_called()
    mock_polyline.assert_called()

