import unittest
from unittest.mock import patch, MagicMock, mock_open
from KAHIT_SAAN import geocoding, create_map

class TestKahitSaan(unittest.TestCase):

    # Test for successful geocoding response (Mocked for Manila, Philippines)
    @patch('builtins.input', side_effect=[
        "Manila, Philippines",  # Starting location (Manila)
        "Vigan, Ilocos Norte",  # Destination location (Vigan)
        "car",                   # Travel mode (car)
        "yes"                    # Generate map (yes)
    ])  
    @patch('requests.get')  # Mock the requests.get method to simulate API calls
    def test_geocoding_and_map_creation(self, mock_get, mock_input):
        # Mock the response from the GraphHopper API for a successful geocoding request for Manila
        mock_geocode_response = MagicMock()
        mock_geocode_response.status_code = 200
        mock_geocode_response.json.return_value = {
            "hits": [
                {
                    "point": {"lat": 14.5995, "lng": 120.9842},  # Coordinates for Manila
                    "name": "Manila",
                    "osm_value": "address",
                    "country": "Philippines",
                    "state": "National Capital Region"
                }
            ]
        }
        mock_get.return_value = mock_geocode_response  # Return mock geocoding response for both locations

        # Mock the response for Vigan, Ilocos Norte
        mock_geocode_response.json.return_value = {
            "hits": [
                {
                    "point": {"lat": 17.5764, "lng": 120.3827},  # Coordinates for Vigan
                    "name": "Vigan",
                    "osm_value": "address",
                    "country": "Philippines",
                    "state": "Ilocos Norte"
                }
            ]
        }

        # Test geocoding for both locations
        orig = geocoding("Manila, Philippines", "your_api_key")
        dest = geocoding("Vigan, Ilocos Norte", "your_api_key")

        # Assert geocoding responses
        self.assertEqual(orig[0], 200)
        self.assertEqual(orig[1], 14.5995)
        self.assertEqual(orig[2], 120.9842)
        self.assertEqual(orig[3], "Manila, National Capital Region, Philippines")

        self.assertEqual(dest[0], 200)
        self.assertEqual(dest[1], 17.5764)
        self.assertEqual(dest[2], 120.3827)
        self.assertEqual(dest[3], "Vigan, Ilocos Norte, Philippines")

        # Now simulate map creation (check if the map file is generated)
        # We will patch the file system check to ensure the map is created
        try:
            with patch('builtins.open', mock_open()) as mock_file:
                create_map(orig, dest, "car")
                mock_file.assert_called_with("KAHIT_SAAN_MAP.html", "r")  # Ensure map file is opened for reading
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
