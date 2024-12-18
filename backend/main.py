# Import necessary libraries
from flask import Flask, request, jsonify  # Flask for creating the web app and handling requests
from flask_cors import CORS  # To handle Cross-Origin Resource Sharing

import os

from httpx import ConnectError

import cvmodel

 # Importing Skyfield functions for astronomical calculations
from skyfield.api import load, N, W, wgs84, Star, Angle 

import pandas as pd  # For data manipulation and analysis

from random import choice  # For selecting a random constellation
import dateutil  # Date utilities for date parsing

# Load star data from a CSV file into a pandas DataFrame
stars = pd.read_csv("stars.csv")

# Function to create a Star object given right ascension (ra) and declination (dec)
def get_star(ra, dec):
    return Star(ra=Angle(degrees=ra), dec=Angle(degrees=dec))  # Return a Star object with specified ra and dec

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Allow CORS requests from React frontend


# Route to receive location data
@app.route("/location", methods=["POST"])
def receive_location():
    data = request.get_json()  # Get the JSON data sent in the request
    latitude = data.get("latitude")  # Extract latitude from the data
    longitude = data.get("longitude")  # Extract longitude from the data

    timestamp = data.get("timestamp")  # Retrieve the timestamp (UTC)
    print(
        f"Received coordinates: Latitude={latitude}, Longitude={longitude}, Time={timestamp}"
    )  # Log the received coordinates and timestamp
    return jsonify(  # Return a JSON response
        {
            "message": "Location and time received",  # Message indicating receipt of data
            "latitude": latitude,  # Return latitude
            "longitude": longitude,  # Return longitude
            "timestamp": timestamp,  # Return the UTC timestamp
        }
    )

# Route to receive visibility data
@app.route("/visible", methods=["POST"])
def receive_visible():
    data = request.get_json()  # Get the JSON data sent in the request
    lat = data.get("latitude")  # Extract latitude from the data
    lng = data.get("longitude")  # Extract longitude from the data
    timestamp = data.get("timestamp")  # Retrieve the timestamp (UTC)

    planets = load("de421.bsp")  # Load the JPL ephemeris DE421
    earth = planets["earth"]

    ts = load.timescale().utc(dateutil.parser.parse(timestamp))  # Create a timescale object with the given timestamp
    loc = earth + wgs84.latlon(lat * N, lng * W)  # Create a location object using the latitude and longitude

    visibleConstellations = []  # Initialize a list to store visible constellations
    print(f"Received coordinates: Latitude={lat}, Longitude={lng}, Time={timestamp}")  # Log the received coordinates and timestamp

    # Loop through each star in the stars DataFrame
    for star in stars.iterrows():

        star = star[1]
        # Observe the star's position from the observer's location at the given time
        starPos = loc.at(ts).observe(get_star(star["ra_degrees"], star["dec_degrees"]))

        # Get the altitude and azimuth of the star
        alt, az, d = starPos.apparent().altaz()

        # Check if the star is above 45 degrees altitude and not already in the list
        if alt.degrees > 45 and star["constellation"] not in visibleConstellations:
            visibleConstellations.append(star["constellation"])  # Add the constellation to the list

    consts = []
    
    for c in visibleConstellations:
        # Find the guide star with the minimum magnitude in the chosen constellation
        df = stars[stars["constellation"] == c]
        guideStar = df.loc[df["magnitude"].idxmin()]

        # Observe the guide star's position
        starPos = loc.at(ts).observe(get_star(guideStar["ra_degrees"], guideStar["dec_degrees"]))

        # Get the altitude and azimuth of the guide star
        alt, az, d = starPos.apparent().altaz()

        # Return a JSON response with the visibility information
        consts.append(
            {
                "message": "Visible constellations",  # Message indicating visible constellations
                "constellation": c,  # Return the selected constellation
                "magnitude": guideStar["magnitude"],  # Return the magnitude of the guide star
                "alt": alt.degrees,  # Return the altitude in degrees
                "az": az.degrees,  # Return the azimuth in degrees
                "timestamp": timestamp,  # Return the UTC timestamp
            }
        )

    return jsonify(consts)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['photo']

    constellation = request.form.get('constellation')
    file.filename += '.jpg'    
    # Save or process the file
    if file and allowed_file(file.filename):  # Optionally, validate file type
        file.save(os.path.join("uploads", file.filename))  # Save file if needed
        # Process the image as needed here, e.g., with OpenCV or PIL

        path = "./uploads/blob.jpg"
        result = cvmodel.test_runner_2(path)
        if result is None:
            match = False
        else:
            match = (result == constellation)
        print(result, constellation, match)
        # Return success message or analysis results
        return jsonify({
            "message": "File uploaded successfully", 
            "matched_constellation": match})
    else:
        return jsonify({"error": "Invalid file"}), 400



# Main entry point for the application
if __name__ == "__main__":
    stars = pd.read_csv("stars.csv")  # Load the star data again before starting the app
    app.run(debug=True, ssl_context='adhoc')  # Run the Flask app in debug mode


