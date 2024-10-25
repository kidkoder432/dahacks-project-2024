from h11 import Data
import numpy as np 
from pandas import DataFrame
from skyfield.api import load
from skyfield.data import hipparcos

from astropy import units as u
from astropy.coordinates import SkyCoord

#Define the right ascension (RA) and declination (Dec) of a start
ra = 10.684 * u.deg
dec = 41.269 * u.deg

#Creates the SkyCoord object for the star coordinates in the ICRS frame
star_coord = SkyCoord(ra, dec, frame="icrs")

#Get the constellation of the defined star coords
constellation = star_coord.get_constellation()

print(constellation)

#Load the Hipparcos star data
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f) #load star data into dataframe

    consts = [] #list to hold constellations of bright stars

    stars_new = DataFrame() #create a new dataframe

    print(stars.shape[0]) #Print the number of stars in the orginal data frame

    for star in stars.iterrows(): #

        if np.isnan(star[1]["ra_degrees"]) or np.isnan(star[1]["dec_degrees"]):
            coord = SkyCoord(ra=0 * u.deg, dec=0 * u.deg)
            loc = star[0]

        else:
            if star[1]["magnitude"] < 5:
                print(star[0], star[1]['magnitude'])
                coord = SkyCoord(ra=star[1]["ra_degrees"] * u.deg, dec=star[1]["dec_degrees"] * u.deg)
                consts.append(coord.get_constellation())

                stars_new = stars_new._append(star[1])
            else:
                loc = star[0]

    stars_new = stars_new.assign(constellation=consts)

    print(stars_new.columns.tolist())

    print(len(stars_new["constellation"].unique()))

    stars_new.to_csv("stars.csv")
    # print(stars_new[stars_new["constellation"] == constellation])
