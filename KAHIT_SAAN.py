import urllib.parse
import requests
import folium
import polyline

# GraphHopper API URL and API Key for routing and geocoding services
route_url = "https://graphhopper.com/api/1/route?"
key = "734ffe9a-d48c-42b2-9b27-a6134a03e697"

def geocoding(location, key):
    
    """
    This function performs geocoding by converting a human-readable location (address or place)
    into geographic coordinates (latitude and longitude) using the GraphHopper geocoding API.

    Args:
    location (str): The location (address, city, etc.) to geocode.
    key (str): The API key for accessing the GraphHopper geocoding API.

    Returns:
        - Status code of the API request (200 for success).
        - Latitude of the location.
        - Longitude of the location.
        - The name of the location.
    """

    while location == "":
        location = input("Enter the location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data.get("hits", [])) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print("Geocoded Location:", new_loc, "(Location Type:", value + ")")
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        print("No results found for:", location)

        if json_status != 200:
            print("Geocode API status: " + str(json_status) +
                  "\nError message: " + json_data.get("message", "Unknown error"))

    return json_status, lat, lng, new_loc


def create_map(orig, dest, vehicle):
    
    """
    This function generates a visual map using Folium, with markers for the origin and destination.

    Args:
    orig (tuple): A tuple containing the origin's latitude, longitude, and name.
    dest (tuple): A tuple containing the destination's latitude, longitude, and name.
    vehicle (str): The vehicle type (e.g., "car", "bike", "foot") used to fetch the route.

    Returns:
    None: The function saves the map as an HTML file in the same folder as the Python App.
    """

    # Create a base map centered around the origin
    m = folium.Map(location=[orig[1], orig[2]], zoom_start=12)

    # Add markers for origin and destination
    folium.Marker(
        [orig[1], orig[2]], popup=f"Origin: {orig[3]}", icon=folium.Icon(color='blue')
    ).add_to(m)

    folium.Marker(
        [dest[1], dest[2]], popup=f"Destination: {dest[3]}", icon=folium.Icon(color='red')
    ).add_to(m)

    # If routing info exists, plot a polyline
    if vehicle:
        op = f"&point={orig[1]},{orig[2]}"
        dp = f"&point={dest[1]},{dest[2]}"
        route_url_with_params = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        route_response = requests.get(route_url_with_params)
        route_data = route_response.json()

        # Plot route as a polyline on the map
        if route_response.status_code == 200:
            # Extract the encoded polyline from the GraphHopper response
            encoded_polyline = route_data["paths"][0]["points"]
            
            # Decode the polyline to get the lat/lng coordinates
            route_points = polyline.decode(encoded_polyline)

            # Add the polyline to the map
            folium.PolyLine(route_points, color="green", weight=5, opacity=0.7).add_to(m)
        else:
            print(f"Error fetching route data: {route_data.get('message', 'Unknown error')}")

    # Save the map to an HTML file
    map_filename = "KAHIT_SAAN_MAP.html"
    m.save(map_filename)
    print(f"\nMap saved as {map_filename}")


while True:
    """
    Main loop for user interaction: The program will repeatedly ask for a starting location and
    a destination, calculate routes for various vehicle profiles (car, bike, foot), and provide
    a map if the user chooses to generate one.
    """
    
    # Get starting location from user
    loc1 = input("\nStarting Location (or 'quit' to exit): ")
    if loc1.lower() in ["quit", "q"]:
        break
    orig = geocoding(loc1, key)

    # Get destination location from user
    loc2 = input("Destination (or 'quit' to exit): ")
    if loc2.lower() in ["quit", "q"]:
        break
    dest = geocoding(loc2, key)

    if orig[0] == 200 and dest[0] == 200 and orig[1] != "null" and dest[1] != "null":
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        # Show distance and duration summary for all vehicle profiles
        print("\n=========================================================================")
        print(f"Distance & Duration Summary from {orig[3]} to {dest[3]}")
        print("===========================================================================")
        profile = ["car", "bike", "foot"]
        available_modes = []  # List to store modes with valid routes

        for mode in profile:
            # Construct the route request URL for each profile
            paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": mode}) + op + dp
            paths_reply = requests.get(paths_url)
            paths_status = paths_reply.status_code
            paths_data = paths_reply.json()

            if paths_status == 200:
                # Calculate the route's distance, time, and print the summary
                km = paths_data["paths"][0]["distance"] / 1000
                miles = km / 1.61
                sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
                mins = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
                hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
                print(f"{mode.title():<5} ➝ {miles:.1f} miles / {km:.1f} km | "
                      f"{hr:02d}:{mins:02d}:{sec:02d}")
                available_modes.append(mode)
            else:
                print(f"{mode.title():<5} ➝ Error: {paths_data.get('message', 'Unknown error')}")

        # Let user choose a vehicle profile for detailed directions
        print("\nAvailable profiles:", ", ".join(available_modes))
        vehicle = input("Choose one profile for detailed directions (or 'quit' to exit): ").lower()
        if vehicle in ["quit", "q"]:
            break
        if vehicle not in available_modes:
            print("Invalid choice, defaulting to car.")
            vehicle = "car"

        # Show step-by-step directions for the selected vehicle
        print("\n====================================================================")
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("======================================================================")
        chosen_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        chosen_data = requests.get(chosen_url).json()

        for each in chosen_data["paths"][0]["instructions"]:
            path = each["text"]
            distance = each["distance"]
            print("{0} ( {1:.1f} km / {2:.1f} miles )".format(
                path, distance / 1000, distance / 1000 / 1.61))

        # Prompt user to generate a map
        generate_map = input("\nWould you like to generate a visual map? (yes/no): ").lower()
        if generate_map in ["yes", "y"]:
            # Generate and save the map
            create_map(orig, dest, vehicle)
        else:
            print("")
        print("====================================================================")
    else:
        print("Routing skipped due to invalid geocoding results.")
