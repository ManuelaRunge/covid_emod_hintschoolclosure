#! /usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime, timedelta
import json


def main(filenames):

    for filename in filenames:
        with open(filename, "r") as handle:
            data = json.load(handle)
        infectious_fraction = data["Channels"]["Infectious Population"]["Data"]
        total_population = data["Channels"]["Statistical Population"]["Data"]
        infectious_population = list(map(lambda f, p: round(f * p), infectious_fraction, total_population))
        maximum = max(infectious_population)
        day = infectious_population.index(maximum)
        date = datetime(2020, 1, 14)
        delta = timedelta(days=day)
        peak = date + delta
        print(f"File: {filename}")
        print(f"      Maximum infectious population is {maximum:6} on day {day:3} ({peak.strftime('%Y/%m/%d')})")

    return

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filenames", nargs="+")
    args = parser.parse_args()
    main(args.filenames)
