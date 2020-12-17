from geopy.distance import distance as geodistance

def find_shortest_distance(needle, haystack):
    shortest = [-1, None]

    for index, location in enumerate(haystack):
        distance = geodistance(needle, location).km

        if not shortest[1]:
            shortest[1] = distance

        if distance < shortest[1]:
            shortest = (index, distance)

    return shortest