# test_KAHIT_SAAN.py
import pytest
from unittest.mock import patch, MagicMock, mock_open
import KAHIT_SAAN

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

valid_geocode_no_state = {
    "hits": [{
        "point": {"lat": 48.8566, "lng": 2.3522},
        "name": "Paris",
        "osm_value": "city",
        "country": "France"
    }]
}

valid_geocode_no_country = {
    "hits": [{
        "point": {"lat": 14.5995, "lng": 120.9842},
        "name": "Manila",
        "osm_value": "city"
    }]
}

invalid_geocode_response = {
    "hits": []
}

valid_route_response = {
    "paths": [{
        "distance": 100000,  # 100 km
        "time": 3600000,  # 1 hour in ms
        "points": "encoded_polyline_data",
        "instructions": [
            {"text": "Turn right", "distance": 500},
            {"text": "Go straight", "distance": 1500}
        ]
    }]
}

invalid_route_response = {
    "message": "Route not found"
}


# Test geocoding with valid location (with state and country)
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_success_with_state(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_geocode_response
    mock_get.return_value = mock_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("Berlin", "fake_api_key")
    
    assert status == 200
    assert lat == 52.52
    assert lng == 13.405
    assert location == "Berlin, Berlin, Germany"


# Test geocoding with valid location (without state)
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_success_no_state(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_geocode_no_state
    mock_get.return_value = mock_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("Paris", "fake_api_key")
    
    assert status == 200
    assert lat == 48.8566
    assert lng == 2.3522
    assert location == "Paris, France"


# Test geocoding with valid location (without country)
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_success_no_country(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_geocode_no_country
    mock_get.return_value = mock_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("Manila", "fake_api_key")
    
    assert status == 200
    assert lat == 14.5995
    assert lng == 120.9842
    assert location == "Manila"


# Test geocoding with invalid location (empty hits)
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_failure_empty_hits(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = invalid_geocode_response
    mock_get.return_value = mock_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("InvalidLocation", "fake_api_key")
    
    assert status == 200
    assert lat == "null"
    assert lng == "null"
    assert location == "InvalidLocation"


# Test geocoding with API error
@patch('KAHIT_SAAN.requests.get')
def test_geocoding_api_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad request"}
    mock_get.return_value = mock_response
    
    status, lat, lng, location = KAHIT_SAAN.geocoding("TestLocation", "fake_api_key")
    
    assert status == 400
    assert lat == "null"
    assert lng == "null"
    assert location == "TestLocation"


# Test create_map function
@patch('KAHIT_SAAN.polyline.decode')
@patch('KAHIT_SAAN.requests.get')
@patch('KAHIT_SAAN.folium.Map')
@patch('KAHIT_SAAN.folium.Marker')
@patch('KAHIT_SAAN.folium.PolyLine')
def test_create_map_success(mock_polyline, mock_marker, mock_map, mock_get, mock_decode):
    # Mock the route API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_route_response
    mock_get.return_value = mock_response
    
    # Mock polyline decode
    mock_decode.return_value = [(52.52, 13.405), (48.8566, 2.3522)]
    
    # Mock the map instance
    mock_map_instance = MagicMock()
    mock_map.return_value = mock_map_instance
    
    orig = (200, 52.52, 13.405, "Berlin")
    dest = (200, 48.8566, 2.3522, "Paris")
    vehicle = "car"
    
    result = KAHIT_SAAN.create_map(orig, dest, vehicle)
    
    # Verify map was created
    mock_map.assert_called_once_with(location=[52.52, 13.405], zoom_start=12)
    
    # Verify markers were added (should be called twice)
    assert mock_marker.call_count == 2
    
    # Verify route was added
    mock_polyline.assert_called_once()
    
    # Verify map was saved
    mock_map_instance.save.assert_called_once_with("static/KAHIT_SAAN_MAP.html")
    
    assert result == "static/KAHIT_SAAN_MAP.html"


# Test create_map with route API failure
@patch('KAHIT_SAAN.requests.get')
@patch('KAHIT_SAAN.folium.Map')
@patch('KAHIT_SAAN.folium.Marker')
def test_create_map_route_failure(mock_marker, mock_map, mock_get):
    # Mock the route API response with error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = invalid_route_response
    mock_get.return_value = mock_response
    
    # Mock the map instance
    mock_map_instance = MagicMock()
    mock_map.return_value = mock_map_instance
    
    orig = (200, 52.52, 13.405, "Berlin")
    dest = (200, 48.8566, 2.3522, "Paris")
    vehicle = "car"
    
    result = KAHIT_SAAN.create_map(orig, dest, vehicle)
    
    # Verify map and markers were still created
    mock_map.assert_called_once()
    assert mock_marker.call_count == 2
    
    # Verify map was saved
    mock_map_instance.save.assert_called_once()


# Test Flask route with valid data
@patch('KAHIT_SAAN.create_map')
@patch('KAHIT_SAAN.geocoding')
@patch('KAHIT_SAAN.requests.get')
def test_home_route_success(mock_get, mock_geocoding, mock_create_map):
    # Mock geocoding responses
    mock_geocoding.side_effect = [
        (200, 52.52, 13.405, "Berlin, Germany"),
        (200, 48.8566, 2.3522, "Paris, France")
    ]
    
    # Mock route API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_route_response
    mock_get.return_value = mock_response
    
    # Mock create_map
    mock_create_map.return_value = "static/KAHIT_SAAN_MAP.html"
    
    with KAHIT_SAAN.app.test_client() as client:
        response = client.post('/', data={
            'start_location': 'Berlin',
            'dest_location': 'Paris',
            'vehicle_mode': 'car'
        })
        
        assert response.status_code == 200
        assert b'Route Summary' in response.data or b'KAHIT SAAN' in response.data


# Test Flask route with missing fields
def test_home_route_missing_fields():
    with KAHIT_SAAN.app.test_client() as client:
        response = client.post('/', data={
            'start_location': 'Berlin',
            'dest_location': '',
            'vehicle_mode': 'car'
        })
        
        assert response.status_code == 200
        assert b'All fields are required' in response.data


# Test Flask route with invalid geocoding
@patch('KAHIT_SAAN.geocoding')
def test_home_route_invalid_location(mock_geocoding):
    # Mock geocoding to return null coordinates
    mock_geocoding.side_effect = [
        (200, "null", "null", "InvalidPlace"),
        (200, 48.8566, 2.3522, "Paris, France")
    ]
    
    with KAHIT_SAAN.app.test_client() as client:
        response = client.post('/', data={
            'start_location': 'InvalidPlace',
            'dest_location': 'Paris',
            'vehicle_mode': 'car'
        })
        
        assert response.status_code == 200
        assert b'Invalid location' in response.data


# Test Flask route with route API failure
@patch('KAHIT_SAAN.geocoding')
@patch('KAHIT_SAAN.requests.get')
def test_home_route_api_failure(mock_get, mock_geocoding):
    # Mock geocoding responses
    mock_geocoding.side_effect = [
        (200, 52.52, 13.405, "Berlin, Germany"),
        (200, 48.8566, 2.3522, "Paris, France")
    ]
    
    # Mock route API failure
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = invalid_route_response
    mock_get.return_value = mock_response
    
    with KAHIT_SAAN.app.test_client() as client:
        response = client.post('/', data={
            'start_location': 'Berlin',
            'dest_location': 'Paris',
            'vehicle_mode': 'car'
        })
        
        assert response.status_code == 200
        assert b'Error fetching route data' in response.data


# Test Flask GET request (initial page load)
def test_home_route_get():
    with KAHIT_SAAN.app.test_client() as client:
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'KAHIT SAAN' in response.data
        assert b'Starting Location' in response.data
        assert b'Destination' in response.data