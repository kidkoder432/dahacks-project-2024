# Import necessary libraries
from flask import Flask, request, jsonify  # Flask for creating the web app and handling requests
from flask_cors import CORS  # To handle Cross-Origin Resource Sharing

import os

 # Importing Skyfield functions for astronomical calculations
from matplotlib.layout_engine import ConstrainedLayoutEngine
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

```import cv2
import numpy as np
from scipy.spatial import KDTree
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
from astropy import units as u

def preprocess_image(image_path):
    # Load image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Threshold to isolate bright spots (stars)
    _, thresholded = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours (stars) in thresholded image
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get star coordinates
    stars = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 5:  # Ignore small noise
            (x, y), _ = cv2.minEnclosingCircle(cnt)
            stars.append((int(x), int(y)))
    
    return stars

def load_known_constellations():
    # Load star data for known constellations
    v = Vizier(columns=["RAJ2000", "DEJ2000", "Constellation"])
    result = v.query_object("Polaris", catalog="I/239/hip_main")
    
    constellation_stars = {}
    for star in result[0]:
        ra = star["RAJ2000"]
        dec = star["DEJ2000"]
        constellation = star["Constellation"]
        
        if constellation not in constellation_stars:
            constellation_stars[constellation] = []
        
        constellation_stars[constellation].append((ra, dec))
        
    return constellation_stars

def match_constellation(stars, constellation_data, threshold=0.05):
    # Check if stars match any known constellation
    star_tree = KDTree(stars)
    matched_constellation = None
    min_distance = float("inf")
    
    for constellation, known_stars in constellation_data.items():
        known_tree = KDTree(known_stars)
        distance, _ = star_tree.query(known_tree.data)
        avg_distance = np.mean(distance)
        
        if avg_distance < min_distance and avg_distance < threshold:
            min_distance = avg_distance
            matched_constellation = constellation
    
    return matched_constellation

def analyze_constellation(image_path):
    stars = preprocess_image(image_path)
    constellation_data = load_known_constellations()
    matched_constellation = match_constellation(stars, constellation_data)
    
    if matched_constellation:
        print(f"Constellation identified: {matched_constellation}")
        return matched_constellation
    else:
        print("No known constellation matched.")
        return None


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
        result = analyze_constellation(path)
        if result is None:
            match = False
        else:
            match = (result == constellation)
        print()
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


