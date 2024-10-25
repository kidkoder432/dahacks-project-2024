from skyfield.api import load
from skyfield.data import hipparcos

from astropy import units as u
from astropy.coordinates import SkyCoord

ra = 10.684 * u.deg
dec = 41.269 * u.deg
star_coord = SkyCoord(ra, dec, frame="icrs")

constellation = star_coord.get_constellation()

print(constellation)

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

    consts = []
    for star in stars.iterrows():
        print(star[0], star[1]['ra_degrees'], star[1]['dec_degrees'])
        coord = SkyCoord(ra=star[1]["ra_degrees"] * u.deg, dec=star[1]["dec_degrees"] * u.deg)

        consts.append(coord.get_constellation())

    stars.assign(constellation=consts)

    print(stars[stars["constellation"] == constellation])
