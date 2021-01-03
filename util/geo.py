from dataknead import Knead
from geopy.distance import distance as geodistance
from shapely.geometry import asShape, Point
from util.utils import dd
import fiona

def find_shortest_distance(needle, haystack, rough = False):
    shortest = [-1, None]

    for index, location in enumerate(haystack):
        if rough:
            # If rough is enabled, get the difference between the coordinates
            # to prevent expensive geodistance calculation
            diff = [
                abs(float(needle[0]) - float(location[0])),
                abs(float(needle[1]) - float(location[1]))
            ]

            # 0.1 is roughly 5 km
            if sum(diff) > 0.1:
                continue

        distance = geodistance(needle, location).km

        if not shortest[1]:
            shortest[1] = distance

        if distance < shortest[1]:
            shortest = (index, distance)

    return shortest

# Find coordinates using a shapefile
# Based on https://stackoverflow.com/a/18749373/152809
class ShapeFinder:
    # path should be a path to a shapefile
    def __init__(self, path):
        print(f"Loading shapefile at {path}")

        # We load the collection, then convert it to a series of polygons we
        # can cache and use for the find_coordinate function
        self.shapes = []

        with fiona.open(path) as collection:
            for feature in collection:
                self.shapes.append({
                    "geometry" : asShape(feature["geometry"]),
                    "properties" : feature["properties"]
                })

        print("Loaded and parsed")

    # Note that this function accepts lat/lon while shapely.Point wants lon/lat!
    def find_coordinate(self, lat, lon):
        print(f"Finding coordinate {lat},{lon}")

        point = Point(lon, lat)

        for shape in self.shapes:
            if shape["geometry"].contains(point):
                return shape

        return None