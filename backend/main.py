# app.py
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
