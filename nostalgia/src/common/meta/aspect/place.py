from src.common.infrastructure.sdf import SDF, join_time
from src.common.meta.aspect import Aspect

import pandas as pd
import numpy as np
from nostalgia.ndf import NDF, get_type_from_registry
from nostalgia.nlp import nlp
from nostalgia.times import parse_date_tz
from nostalgia.utils import haversine


class Place(NDF, Aspect):
    keywords = [
        "did i go",
        "i was in",
        "i was at",
        "was i",
        "what place",
        "place",
        "i was at",
        "visit",
        "go",
        "have i been",
        "stay",
    ]
    home = []
    work = []
    hometown = []

    @nlp("filter", "at home")
    def at_home(self):
        return self.__class__(self[self.category == "Home"])

    @nlp("filter", ["near home", "around home"])
    def near_home(self, distance=1000):
        return self.near_(distance, get_type_from_registry("places").at_home)

    @nlp("filter", "at work")
    def at_work(self):
        return self.__class__(self[self.category == "Work"])

    @nlp("filter", ["near work", "around work"])
    def near_work(self, distance=1000):
        return self.near_(distance, get_type_from_registry("places").at_work)

    @property
    def at_hometown(self):
        raise ValueError("Fix me")
        return self.__class__(self[self.city == "Hometown"])

    def near_(self, distance_in_meters, other_places=None):
        places = get_type_from_registry("places") if other_places is None else other_places
        nearbies = []
        for _, row in places[["lat", "lon"]].drop_duplicates().iterrows():
            nearbies.append(haversine(self.lat, self.lon, *row) < distance_in_meters)
        return self.__class__(self[np.any(nearbies, axis=0)])

    def at(self, time):
        mp = parse_date_tz(time)
        return self[self.index.overlaps(pd.Interval(mp.start_date, mp.end_date))]

    @nlp("end", "how much")
    def sum(self):
        return self.distance.sum()

    @nlp("end", "how long", "how much time")
    def length(self):
        return (self.index.right - self.index.left).to_pytimedelta().sum()

    @nlp("filter", "travel")
    def travel(self):
        return self[self.transporting]

    @nlp(
        "filter",
        "drive",
        "by car",
        "travel by car",
        "travel using the car",
        "by car",
        "going by car",
        "on a car",
        "driving",
    )
    def travel_by_car(self):
        return self.col_contains("Driving", "category")

    @nlp(
        "filter",
        "drive by bus",
        "by bus",
        "travel by bus",
        "using the bus",
        "going by bus",
        "on a bus",
    )
    def travel_by_bus(self):
        return self.col_contains("On a bus", "category")

    @nlp(
        "filter",
        "drive by train",
        "by train",
        "travel by train",
        "using the train",
        "going by train",
        "on a train",
    )
    def travel_by_train(self):
        return self.col_contains("On a train", "category")

    @nlp("filter", "work days", "work-days", "on working days")
    def work_days(self):
        return self[self.time.dt.weekday < 5]

    @nlp("filter", "during work", "during work hours")
    def work_hours(self):
        return self[self._office_hours]

    @nlp("end", "address of", "what is the address", "how to find", "how can i find")
    def what_address(self):
        return self["address"]

    def when_at(self, other, **window_kwargs):
        if isinstance(other, str):
            other = get_type_from_registry("places").containing(other)
        return self.__class__(join_time(other, self, **window_kwargs))

    when = when_at

    def near(self, s):
        if isinstance(s, SDF) and s.df_name.endswith("places"):
            selection = s
        else:
            selection = get_type_from_registry("places").containing(s)
        return self.when_at(selection)

    def to_place(self):
        results = []
        places = get_type_from_registry("places")
        for time in self.time:
            try:
                results.append(places.iloc[places.index.get_loc(time)].iloc[0])
            except (TypeError, KeyError):
                pass
        return places.__class__(results)

    def in_a(self, s):
        return self.near(s)

    @property
    def at_home(self):
        self.take_from("places", "category")
        return self[self["places_category"] == "Home"]

    @property
    def at_work(self):
        self.take_from("places", "category")
        return self[self["places_category"] == "Work"]

    def at(self, time_or_place):
        if isinstance(time_or_place, SDF) and time_or_place.df_name.endswith("places"):
            return self.when_at(time_or_place)
        if isinstance(time_or_place, str):
            mp = parse_date_tz(time_or_place)
            if mp:
                start = mp.start_date
                end = mp.end_date
                return self.at_time(start, end)
            else:
                return self.when_at(get_type_from_registry("places").containing(time_or_place))
        raise ValueError("neither time nor place was passed")
