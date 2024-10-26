import pandas as pd
import geocoder
from skyfield.api import load, N, W, wgs84, Star, Angle


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

loc = earth + wgs84.latlon(lat * N, lng * W)


visibleConstellations = []

for star in df.iterrows():
    star = star[1]
    starPos = loc.at(t).observe(get_star(star["ra_degrees"], star["dec_degrees"]))

    alt, az, d = starPos.apparent().altaz()

    if alt.degrees > 45 and star["constellation"] not in visibleConstellations:
        visibleConstellations.append(star["constellation"])

print(visibleConstellations)

star_ra = df.loc[50, "ra_degrees"]
star_dec = df.loc[50, "dec_degrees"]

print(star_ra, star_dec)

star = Star(ra=Angle(degrees=star_ra), dec=Angle(degrees=star_dec))


starPos = loc.at(t).observe(star)

alt, az, d = starPos.apparent().altaz()

print("Altitude:", alt)
print("Azimuth:", az)
print("constellation: " + df.loc[50, "constellation"])

if alt.degrees > 45:
    print(
        f"The constellation {df.loc[50, 'constellation']} is currently visible in the sky!"
    )
else:
    print(
        f"The constellation {df.loc[50, 'constellation']} is not currently visible in the sky."
    )
