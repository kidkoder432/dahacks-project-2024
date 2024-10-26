# app.py
import dateutil.parser
from flask import Flask, request, jsonify
from flask_cors import CORS
from skyfield.api import load, N, W, wgs84, Star, Angle

import pandas as pd

from random import choice
import dateutil

stars = pd.read_csv("stars.csv")


def get_star(ra, dec):
    return Star(ra=Angle(degrees=ra), dec=Angle(degrees=dec))


app = Flask(__name__)
CORS(app)  # Allow CORS requests from React


@app.route("/location", methods=["POST"])
def receive_location():
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    timestamp = data.get("timestamp")  # Retrieve the timestamp (UTC)
    print(
        f"Received coordinates: Latitude={latitude}, Longitude={longitude}, Time={timestamp}"
    )
    return jsonify(
        {
            "message": "Location and time received",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,  # Returning the UTC timestamp
        }
    )


@app.route("/visible", methods=["POST"])
def receive_visible():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")
    timestamp = data.get("timestamp")  # Retrieve the timestamp (UTC)

    ts = load.timescale()
    t = ts.utc(dateutil.parser.parse(timestamp))
    loc = wgs84.latlon(lat * N, lng * W)

    visibleConstellations = []
    print(f"Received coordinates: Latitude={lat}, Longitude={lng}, Time={timestamp}")

    for star in stars:
        starPos = loc.at(t).observe(get_star(star["ra_degrees"], star["dec_degrees"]))

        alt, az, d = starPos.apparent().altaz()

        if alt > 45 and star["constellation"] not in visibleConstellations:
            visibleConstellations.append(star["constellation"])

    c = choice(visibleConstellations)

    guideStar = stars[stars["constellation"] == c].loc[df["magnitude"].idxmin()]

    starPos = loc.at(ts).observe(get_star(guideStar["ra_degrees"], guideStar["dec_degrees"]))

    alt, az, d = starPos.apparent().altaz()

    return jsonify(
        {
            "message": "Visible constellations",
            "constellation": c,
            "magnitude": guideStar["magnitude"],
            "alt": alt.degrees,
            "az": az.degrees,
            "timestamp": timestamp,

        }
    )


if __name__ == "__main__":
    stars = pd.read_csv("stars.csv")
    app.run(debug=True)
