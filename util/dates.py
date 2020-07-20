import re

CIRCA = re.compile("^(?:ca|circa|omstreeks|rond)\.? (\d{4})$")
CENTURY = re.compile("^(\d{2})d?e eeuw$")
RANGE = re.compile("^(\d{4}) ?- ?(\d{4})$")
TOKENS = re.compile(",| en")
YEAR = re.compile("^(\d{4})$")

def check(regex, string):
    matches = regex.findall(string)
    if matches:
        return matches[0]
    else:
        return None

def parse_year_nl_single(date):
    century = check(CENTURY, date)
    if century:
        return (f"{century}00", "century")

    circa = check(CIRCA, date)
    if circa:
        return (circa, "circa")

    year_range = check(RANGE, date)
    if year_range:
        return ([year_range[0], year_range[1]], "range")

    year = check(YEAR, date)
    if year:
        return (year, "year")

    return None

def parse_year_nl(date):
    date = date.strip().lower()

    # Check if we have multiple dates, and if so, return them all
    tokens = [t.strip() for t in TOKENS.split(date)]
    parsed_tokens = [parse_year_nl_single(t) for t in tokens]
    return [t for t in parsed_tokens if t]