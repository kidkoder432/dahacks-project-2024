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


    #Itterates over each star in the dataframe
    for star in stars.iterrows(): 

        #Checks if RA or Dec values are NaN
        if np.isnan(star[1]["ra_degrees"]) or np.isnan(star[1]["dec_degrees"]):
            #creates default coordinate if data mising
            coord = SkyCoord(ra=0 * u.deg, dec=0 * u.deg)
            loc = star[0] #stores index of star

        else:
            #check if stars magnitude is less than 5
            if star[1]["magnitude"] < 5:
                print(star[0], star[1]['magnitude']) #Print star index and magnitude

                #Creates the SkyCoord object for the star coordinates in the ICRS frame
                coord = SkyCoord(ra=star[1]["ra_degrees"] * u.deg, dec=star[1]["dec_degrees"] * u.deg)

                #Get the constellation of the defined star coords
                consts.append(coord.get_constellation())

                #Add the star to the new dataframe
                stars_new = stars_new._append(star[1])
            else:
                loc = star[0] #stores index of star

    
    #add a new colloumn of constellations to the new dataframe
    stars_new = stars_new.assign(constellation=consts)

    #prints constellations of selected stars
    print(stars_new.columns.tolist())

    print(len(stars_new["constellation"].unique()))

    stars_new.to_csv("stars.csv")
    # print(stars_new[stars_new["constellation"] == constellation])
