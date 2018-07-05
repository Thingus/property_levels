import requests
import gdal
# import sentienlsat
import matplotlib.pyplot as plt
import configparser
import json
import numpy
import ogr


def request_area_prices(area, api_key):
    """Returns a of prices from area. Looks like it's paginated."""
    api_request = r"http://api.zoopla.co.uk/api/v1/property_listings.json?api_key={}&area={}".format(api_key, area)
    response = requests.get(api_request)
    out = json.loads(response.content)
    return out


def extract_prices_and_coords(results):
    """Builds a list of a set of lat-lons and property prices from the results of a Zoopla search"""
    out = []
    for listing in results["listing"]:
        out.append([
            listing['latitude'],
            listing['longitude'],
            int(listing['price'])
        ])
    return out


def create_wkt_from_coords(coords):
    points = ogr.Geometry(ogr.wkbMultiPoint)
    for coord in coords:
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(coord[0], coord[1])
        points.AddGeometry(point)
    return points.ExportToWkt()


def



if __name__ == "__main__":

    conf = configparser.ConfigParser()
    conf.read("conf.ini")
    api_key = conf["zoopla"]["api_key"]
    town = conf["property_levels"]["town"]
    results = request_area_prices(town, api_key)
    coords = extract_prices_and_coords(results)
    print(create_wkt_from_coords(coords))


    #OK, from the Zoopla API web interface; we have property price and lat-lon as -180 -180, 90, -90. We good.
    # Oooooh, it also gives you a bounding box! How nice ^_^
    # Listing is the element for individual properties
