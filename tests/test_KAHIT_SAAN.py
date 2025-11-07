import unittest
from unittest.mock import patch, MagicMock, mock_open
from KAHIT_SAAN import geocoding, create_map

class TestKahitSaan(unittest.TestCase):

    # Test for geocoding and map creation
    @patch('builtins.input', side_effect=[
        "University of Santo Tomas, Manila",  # Starting location (UST, Manila)
        "SM North Edsa, Quezon City",  # Destination location (SM North Edsa, Quezon City)
        "car",                   # Travel mode (car)
        "yes"                    # Generate map (yes)
    ])  
    @patch('requests.get')  # Mock the requests.get method to simulate API calls
    def test_geocoding_and_map_creation(self, mock_get, mock_input):
        # Mock the response for University of Santo Tomas, Manila
        mock_ust_response = MagicMock()
        mock_ust_response.status_code = 200
        mock_ust_response.json.return_value = {
            "hits": [
                {
                    "point": {"lat": 14.6000, "lng": 120.9822},  # Coordinates for UST, Manila
                    "name": "University of Santo Tomas",
                    "osm_value": "address",
                    "country": "Philippines",
                    "state": "National Capital Region"
                }
            ]
        }
        
        # Mock the response for SM North Edsa, Manila
        mock_sm_north_response = MagicMock()
        mock_sm_north_response.status_code = 200
        mock_sm_north_response.json.return_value = {
            "hits": [
                {
                    "point": {"lat": 14.6535, "lng": 121.0305},  # Coordinates for SM North Edsa, Quezon City
                    "name": "SM North Edsa",
                    "osm_value": "address",
                    "country": "Philippines",
                    "state": "National Capital Region"
                }
            ]
        }

        # Set the mock responses to be returned for the two geocoding calls
        mock_get.side_effect = [mock_ust_response, mock_sm_north_response]  # First call returns UST, second returns SM North Edsa

        # Mock the response for the route (for map generation)
        mock_route_response = MagicMock()
        mock_route_response.status_code = 200
        mock_route_response.json.return_value = {
            "paths": [
                {
                    "distance": 5000,  # Dummy data for distance
                    "time": 900,  # Dummy data for time
                    "instructions": "Continue straight to SM North Edsa"  # Dummy instructions
                }
            ]
        }
        mock_get.return_value = mock_route_response  # Return the mocked route response

        # Test geocoding for both locations
        orig = geocoding("University of Santo Tomas, Manila", "your_api_key")
        dest = geocoding("SM North Edsa, Quezon City", "your_api_key")

        # Assertions for geocoding responses
        self.assertEqual(orig[0], 200)
        self.assertEqual(orig[1], 14.6000)  # UST latitude
        self.assertEqual(orig[2], 120.9822)  # UST longitude
        self.assertEqual(orig[3], "University of Santo Tomas, National Capital Region, Philippines")

        self.assertEqual(dest[0], 200)
        self.assertEqual(dest[1], 14.6535)  # SM North Edsa latitude
        self.assertEqual(dest[2], 121.0305)  # SM North Edsa longitude
        self.assertEqual(dest[3], "SM North Edsa, National Capital Region, Philippines")

        # Now simulate map creation (check if the map file is generated)
        try:
            with patch('builtins.open', mock_open()) as mock_file:
                create_map(orig, dest, "car")
                # Ensure that the map file is being opened for writing and not reading
                mock_file.assert_called_with("KAHIT_SAAN_MAP.html", "w")  # Ensure map file is opened for writing
        except Exception as e:
            self.fail(f"Map file creation failed with error: {e}")

    # Additional test for geocoding failure (mocked)
    @patch('builtins.input', side_effect=["Invalid Location", "Invalid Location"])
    @patch('requests.get')
    def test_geocoding_failure(self, mock_get, mock_input):
        # Simulate a failed geocoding response (404 Not Found)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_get.return_value = mock_response  # Mock the API response for failure

        # Call geocoding for invalid locations
        status, lat, lng, location = geocoding("Invalid Location", "your_api_key")
        
        # Assertions for failed geocoding
        self.assertEqual(status, 404)
        self.assertEqual(lat, "null")
        self.assertEqual(lng, "null")
        self.assertEqual(location, "Invalid Location")

# Running the tests
if __name__ == '__main__':
    unittest.main()
