from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS requests from React

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    timestamp = data.get('timestamp')  # Retrieve the timestamp (UTC)
    print(f"Received coordinates: Latitude={latitude}, Longitude={longitude}, Time={timestamp}")
    return jsonify({
        "message": "Location and time received",
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp  # Returning the UTC timestamp
    })


if __name__ == '__main__':
    app.run(debug=True)
'''
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # To make requests to the astronomy API

app = Flask(__name__)
CORS(app)  # Allow CORS requests from React

# Replace with actual astronomy API URL and your API key
ASTRONOMY_API_URL = "https://api.astronomyapi.com/api/v2/bodies/constellations"
API_KEY = "6e801b79-e87a-42d9-bc63-442b3ea921a2"

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    timestamp = data.get('timestamp')  # Retrieve the timestamp (UTC)
    print(f"Received coordinates: Latitude={latitude}, Longitude={longitude}, Time={timestamp}")

    # Fetch visible constellations from Astronomy API
    try:
        response = requests.get(
            ASTRONOMY_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={
                "latitude": latitude,
                "longitude": longitude,
                "datetime": timestamp
            }
        )
        constellation_data = response.json()
        print("Constellation data:", constellation_data)
        # Extract constellation details
        constellations = []
        if "constellations" in constellation_data:
            constellations = [
                {
                    "name": constellation["name"],
                    "best_viewing_time": constellation.get("bestViewingTime", "N/A"),  # Adapt based on API response structure
                    "description": constellation.get("description", "No description available."),
                    "image_url": constellation.get("image", "https://via.placeholder.com/150")  # Use a placeholder if no image
                }
                for constellation in constellation_data["constellations"]
            ]

        return jsonify({
            "message": "Location and time received",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
            "constellations": constellations
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
'''
# app.py


