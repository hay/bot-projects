from datetime import datetime
from pywikibot import WbTime
import locale
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

"""
Parses ISO 8601 formatted dates (without time, e.g. 2001-03-09) to
day, month and year, and also to English and Dutch friendly strings
"""
def parse_isodate(isodate):
    date = datetime.strptime(isodate, "%Y-%m-%d")

    locale.setlocale(locale.LC_TIME, "en_US")
    en = date.strftime("%B %-d, %Y")
    locale.setlocale(locale.LC_TIME, "nl_NL")
    nl = date.strftime("%-d %B %Y")

    return {
        "day" : date.day,
        "en" : en,
        "iso" : isodate,
        "month" : date.month,
        "nl" : nl,
        "year" : date.year
    }

"""
This expects a partial ISO8601 date, which will be parsed to either
year, month or day,
e.g. 2015 -> 2015, year
     05-2015 -> may 2015, month
     07-05-2015 -> may 7th, day
"""
def partial_date_to_wbtime(date):
    if len(date) == 4:
        return WbTime(year = int(date))
    elif len(date) == 7:
        month, year = date.split("-")
        return WbTime(year = int(year), month = int(month))
    elif len(date) == 10:
        day, month, year = date.split("-")
        return WbTime(day = int(day), month = int(month), year = int(year))
    else:
        raise TypeError(f"Invalid date to parse: {date}")

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