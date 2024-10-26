import pandas as pd
import geocoder
from skyfield.api import load, N, E, wgs84, Star, Angle

from random import choice


def get_current_gps_coordinates():
    g = geocoder.ip(
        "me"
    )  # this function is used to find the current information using our IP Add
    if g.latlng is not None:  # g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None


df = pd.read_csv("stars.csv")

print(len(df["constellation"].unique()))

print(df["constellation"].unique())


def get_star(ra, dec):
    return Star(ra=Angle(degrees=ra), dec=Angle(degrees=dec))


ts = load.timescale()
t = ts.now()

planets = load("de421.bsp")

earth = planets["earth"]

lat, lng = get_current_gps_coordinates()

loc = earth + wgs84.latlon(lat * N, lng * E)

print(loc)
print(lat, lng)
print(t)

visibleConstellations = []

for star in df.iterrows():
    star = star[1]
    starPos = loc.at(t).observe(get_star(star["ra_degrees"], star["dec_degrees"]))

    alt, az, d = starPos.apparent().altaz()

    if alt.degrees > 45 and star["constellation"] not in visibleConstellations:
        visibleConstellations.append(star["constellation"])

# print(visibleConstellations)

c = choice(visibleConstellations)

constellationStarDf = df[df["constellation"] == c]
# Find the guide star with the minimum magnitude in the chosen constellation
guideStar = constellationStarDf.loc[constellationStarDf["magnitude"].idxmin()]

print(guideStar["ra_degrees"], guideStar["dec_degrees"])

# Observe the guide star's position
starPos = loc.at(t).observe(get_star(guideStar["ra_degrees"], guideStar["dec_degrees"]))

# Get the altitude and azimuth of the guide star
alt, az, d = starPos.apparent().altaz()
print(
    f"Constellation: {c}, Altitude: {alt}, Azimuth: {az} is visible in the sky!"
)
