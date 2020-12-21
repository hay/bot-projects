from geopy.distance import distance as geodistance

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