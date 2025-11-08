from flask import Flask, render_template, request, jsonify
import urllib.parse
import requests
import folium
import polyline
import os

# GraphHopper API URL and API Key for routing and geocoding services
route_url = "https://graphhopper.com/api/1/route?"
key = "734ffe9a-d48c-42b2-9b27-a6134a03e697"

app = Flask(__name__)

def geocoding(location, key):
    """
    This function performs geocoding by converting a human-readable location (address or place)
    into geographic coordinates (latitude and longitude) using the GraphHopper geocoding API.
    """
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
    else:
        lat = "null"
        lng = "null"
        new_loc = location

    return json_status, lat, lng, new_loc

def create_map(orig, dest, vehicle):
    """
    This function generates a visual map using Folium, with markers for the origin and destination.
    """
    m = folium.Map(location=[orig[1], orig[2]], zoom_start=12)

    folium.Marker([orig[1], orig[2]], popup=f"Origin: {orig[3]}", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([dest[1], dest[2]], popup=f"Destination: {dest[3]}", icon=folium.Icon(color='red')).add_to(m)

    if vehicle:
        op = f"&point={orig[1]},{orig[2]}"
        dp = f"&point={dest[1]},{dest[2]}"
        route_url_with_params = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        route_response = requests.get(route_url_with_params)
        route_data = route_response.json()

        if route_response.status_code == 200:
            encoded_polyline = route_data["paths"][0]["points"]
            route_points = polyline.decode(encoded_polyline)
            folium.PolyLine(route_points, color="green", weight=5, opacity=0.7).add_to(m)
        else:
            print(f"Error fetching route data: {route_data.get('message', 'Unknown error')}")

    # Save the map to a file in the 'static' folder
    map_filename = "static/KAHIT_SAAN_MAP.html"
    m.save(map_filename)
    return map_filename

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        loc1 = request.form["start_location"]
        loc2 = request.form["dest_location"]
        vehicle = request.form["vehicle_mode"].lower()

        if not loc1 or not loc2 or not vehicle:
            return render_template("index.html", error="All fields are required.")

        # Perform geocoding for both locations
        orig = geocoding(loc1, key)
        dest = geocoding(loc2, key)

        if orig[0] == 200 and dest[0] == 200 and orig[1] != "null" and dest[1] != "null":
            op = f"&point={orig[1]}%2C{orig[2]}"
            dp = f"&point={dest[1]}%2C{dest[2]}"
            
            # Request route data for vehicle mode
            route_url_with_params = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
            route_response = requests.get(route_url_with_params)
            route_data = route_response.json()

            if route_response.status_code == 200:
                km = route_data["paths"][0]["distance"] / 1000
                miles = km / 1.61
                sec = int(route_data["paths"][0]["time"] / 1000 % 60)
                mins = int(route_data["paths"][0]["time"] / 1000 / 60 % 60)
                hr = int(route_data["paths"][0]["time"] / 1000 / 60 / 60)

                # Generate the map
                map_filename = create_map(orig, dest, vehicle)

                # Extract the step-by-step route instructions
                instructions = []
                for each in route_data["paths"][0]["instructions"]:
                    path = each["text"]
                    distance = each["distance"]
                    instructions.append(f"{path} ({distance / 1000:.1f} km / {distance / 1000 / 1.61:.1f} miles)")

                return render_template("index.html", 
                                       start_location=loc1, 
                                       dest_location=loc2, 
                                       vehicle_mode=vehicle, 
                                       result=f"Route: {miles:.1f} miles / {km:.1f} km | {hr:02d}:{mins:02d}:{sec:02d}",
                                       instructions=instructions,
                                       map_filename=map_filename)
            else:
                return render_template("index.html", error="Error fetching route data.")
        else:
            return render_template("index.html", error="Invalid location(s), please try again.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
