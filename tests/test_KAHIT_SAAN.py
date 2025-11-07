import unittest
from unittest.mock import patch, MagicMock
from ..KAHIT_SAAN import geocoding, create_map


class TestKahitSaan(unittest.TestCase):
    
    @patch('requests.get')
    def test_geocoding_success(self, mock_get):
        # Mock the response from the GraphHopper API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "point": {"lat": 12.34, "lng": 56.78},
                    "name": "Test Location",
                    "osm_value": "address",
                    "country": "CountryName",
                    "state": "StateName"
                }
            ]
        }
        mock_get.return_value = mock_response

        status, lat, lng, location = geocoding("Test Location", "your_api_key")
        
        self.assertEqual(status, 200)
        self.assertEqual(lat, 12.34)
        self.assertEqual(lng, 56.78)
        self.assertEqual(location, "Test Location, StateName, CountryName")

    @patch('requests.get')
    def test_geocoding_failure(self, mock_get):
        # Simulate a failure in the API call
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_get.return_value = mock_response

        status, lat, lng, location = geocoding("Invalid Location", "your_api_key")
        
        self.assertEqual(status, 404)
        self.assertEqual(lat, "null")
        self.assertEqual(lng, "null")
        self.assertEqual(location, "Invalid Location")

    @patch('requests.get')
    def test_create_map(self, mock_get):
        # Simulate successful route data fetching
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "paths": [
                {"points": "encoded_polyline_string", "instructions": []}
            ]
        }
        mock_get.return_value = mock_response

        # Test creating a map, should not raise errors
        orig = (200, 12.34, 56.78, "Origin Location")
        dest = (200, 34.56, 78.90, "Destination Location")
        create_map(orig, dest, "car")

        # Here we assume that `create_map` writes a file, check if the file is created
        try:
            with open("KAHIT_SAAN_MAP.html", "r") as file:
                file_content = file.read()
                self.assertTrue(file_content)
        except FileNotFoundError:
            self.fail("Map file was not created.")

if __name__ == '__main__':
    unittest.main()
