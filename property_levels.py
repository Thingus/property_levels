import requests
import gdal
# import sentienlsat
import matplotlib.pyplot as plt
import configparser
import json
import numpy as np
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
    """Creates a multipoint geometry from coords"""
    points = ogr.Geometry(ogr.wkbMultiPoint)
    for coord in coords:
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(coord[0], coord[1])
        points.AddGeometry(point)
    return points.ExportToWkt()


def xyz_from_coords(coords):
    """Returns three arrays (x,y and z) from coords"""
    coords = np.stack(coords, 0)
    x, y, z = np.split(coords, 3, axis=1)
    x, y, z = [foo.flatten() for foo in (x, y, z)]
    return x,y,z

def raster_from_coords(coords, height, width):
    """Returns a 2D image raster of dims height and width from coords."""
    x,y,z = xyz_from_coords(coords)
    x_res_conversion_factor = (max(x) - min(x))/width
    y_res_conversion_factor = (max(y) - min(y))/height
    x_pixels = [int((x_lat - min(x))*x_res_conversion_factor) for x_lat in x]
    y_pixels = [int((y_lon - min(y))*y_res_conversion_factor) for y_lon in y]
    out = np.zeros([width, height]) # Keeping it in gdal order [y, x]
    for index, z_value in enumerate(z):
        out[y_pixels[index], x_pixels[index]] = z[index]
    return out


def contours_from_coords(coords):
    """Plots contours from coordinates"""
    x, y, _ = xyz_from_coords(coords)
    z = raster_from_coords(coords, 1000, 1000)
    print(np.meshgrid(x,y))
    plt.contour(x, y, z)
    plt.show()


if __name__ == "__main__":

    conf = configparser.ConfigParser()
    conf.read("conf.ini")
    api_key = conf["zoopla"]["api_key"]
    town = conf["property_levels"]["town"]
    results = request_area_prices(town, api_key)
    coords = extract_prices_and_coords(results)
    print(create_wkt_from_coords(coords))
    contours_from_coords(coords)


    #OK, from the Zoopla API web interface; we have property price and lat-lon as -180 -180, 90, -90. We good.
    # Oooooh, it also gives you a bounding box! How nice ^_^
    # Listing is the element for individual properties
