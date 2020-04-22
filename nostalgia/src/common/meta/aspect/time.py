import dateparser

from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
import tzlocal
from dateutil.relativedelta import relativedelta
from metadate import is_mp
from metadate import parse_date, Units
from pytz import timezone

from nostalgia.nlp import nlp
from nostalgia.times import now, yesterday, last_week, last_month, last_year, parse_date_tz
from nostalgia.src.common.meta.aspect import Aspect

from nostalgia.ndf import ab_overlap_c
from nostalgia.ndf import ab_overlap_cd

tz = tzlocal.get_localzone()
utc = timezone("UTC")


class Time(Aspect):

    ####
    #  TODO Constructional
    ###

    @classmethod
    def of_duration(cls, time_column: str, duration_column: str, duration_unit: str = "s"):
        return lambda df: df[time_column] - pd.to_timedelta(df[duration_column], unit=duration_unit)

    @classmethod
    def apply(cls, series: pd.Series):
        return pd.to_datetime(series, infer_datetime_format=True)

    @property
    def time(self):
        if not self.inferred_time:
            self.infer_time_range()
        if self._time_col == "time":
            return self._get_item_cache(self._time_col)
        if self._time_col not in self:
            return None
        return getattr(self, self._time_col)

    @property
    def start(self):
        if not self.inferred_time:
            self.infer_time_range()
        if self._start_col == "start":
            return self._get_item_cache(self._start_col)
        if self._start_col not in self:
            return None
        return getattr(self, self._start_col)

    @property
    def end(self):
        if not self.inferred_time:
            self.infer_time_range()
            self.inferred_time = True
        if self._end_col == "end":
            return self._get_item_cache(self._end_col)
        if self._end_col not in self:
            return None
        return getattr(self, self._end_col)

    def infer_time_range(self):
        ####
        #   TODO Results
        ###
        if self.__class__.__name__ == "Results":
            self._start_col, self._time_col, self._end_col = "start", "start", "end"
            return
        time_columns = self.find_time_columns()
        num_times = len(time_columns)
        if num_times == 0:
            self._start_col, self._time_col, self._end_col = None, None, None
        elif num_times == 1:
            self._start_col, self._time_col, self._end_col = None, time_columns[0], None
        elif num_times == 2:
            col1, col2 = time_columns
            sub = self[self[col1].notnull() & self[col2].notnull()]
            a, b = sub[col1], sub[col2]
            if (a >= b).all():
                col1, col2 = col2, col1
            elif not (a <= b).all():
                raise ValueError("Not strictly one col higher than other with dates, can't determine")
            if col1 == "end" and col2 == "start":
                col2, col1 = col1, col2
            self._start_col, self._time_col, self._end_col = col1, col1, col2
            interval_index = pd.IntervalIndex.from_arrays(self[self._start_col], self[self._end_col])
            self.set_index(interval_index, inplace=True)
            self.sort_index(inplace=True)
            self.inferred_time = True
        else:
            msg = "infer time failed: there can only be 1 or 2 datetime columns at the same granularity."

            raise Exception(msg + " Found: " + str(time_columns))

    def find_time_columns(self):
        time_columns = [x for x, y in zip(self.columns, self.dtypes) if "datetime" in str(y)]
        time_granularity_per_column = [self.time_level(self[x]) for x in time_columns]
        if not time_granularity_per_column:
            raise ValueError(
                f"Either 1 or 2 columns should be of type datetime for {self.__class__.__name__} (0 found)"
            )
        max_level = max(time_granularity_per_column)
        # workaround
        # start: 10:00:00
        # end:   10:00:59
        time_columns = [
            t
            for t, l in zip(time_columns, time_granularity_per_column)
            if l == max_level or (l == 2 and max_level == 3)
        ]
        return time_columns

    def at_time(self, start, end=None, sort_diff=True, **window_kwargs):
        if is_mp(start):
            start = start.start_date
            end = start.end_date
        elif isinstance(start, str) and end is None:
            mp = parse_date_tz(start)
            start = mp.start_date
            end = mp.end_date
        elif isinstance(start, str) and isinstance(end, str):
            mp = parse_date_tz(start)
            start = mp.start_date
            mp = parse_date_tz(end)
            end = mp.end_date
        elif end is None and window_kwargs:
            end = start
        elif end is None:
            raise ValueError("Either a metaperiod, a date string, 2 times, or time + window_kwargs.")
        self.infer_time_range()
        if window_kwargs:
            start = start - pd.Timedelta(**window_kwargs)
            end = end + pd.Timedelta(**window_kwargs)
        if self._start_col is None:
            res = self[ab_overlap_c(start, end, self[self._time_col])]
        else:
            res = self[ab_overlap_cd(self[self._start_col], self[self._end_col], start, end)]
        if not res.empty and sort_diff:
            # avg_time = start + (end - start) / 2
            # res["sort_score"] = -abs(res[self._time_col] - avg_time)
            # res = res.sort_values('sort_score').drop('sort_score', axis=1)
            res["sort_score"] = res[self._time_col]
            res = res.sort_values("sort_score").drop("sort_score", axis=1)
        return self.__class__(res)

    def time_level(self, col):
        if (col.dt.microsecond != 0).any():
            return 4
        if (col.dt.second != 0).any():
            return 3
        if (col.dt.minute != 0).any():
            return 2
        if (col.dt.hour != 0).any():
            return 1
        return 0

    ####
    #  TODO Filtering
    ###

    def duration_longer_than(self, **timedelta_kwargs):
        """
                sdf = ExampleSource().build_sdf()
                sd.du
        """
        return self[(self.end - self.time) >= timedelta(**timedelta_kwargs)]

    def duration_shorter_than(self, **timedelta_kwargs):
        return self[(self.end - self.time) <= timedelta(**timedelta_kwargs)]

    @property
    def _working_days(self):
        return self.time.dt.weekday < 5

    @property
    def _working_hours(self):
        if (self.time.dt.hour == 0).all():
            raise ValueError("Hours are not set, thus unreliable. Use `office_days` instead?")
        if self.start is not None:
            return np.array([(8 <= x <= 17 and 8 <= y <= 17) for x, y in zip(self.start.dt.hour, self.end.dt.hour)])
        return np.array([(8 <= x <= 17) for x in self.time.dt.hour])

    @property
    def in_working_days(self):
        return self[self._working_days]

    @property
    def in_working_hours(self):
        return self[self._working_hours]

    @property
    def during_working_hours(self):
        return self[self._working_hours & self._working_days]

    @property
    def outside_working_hours(self):
        return self[~(self._working_hours & self._working_days)]

    @property
    def when_asleep(self):
        return self.__class__(join_time(registry["sleep"].asleep, self))

    def at_night(self, start=22, end=8):
        return self.between_hours(start, end)

    def between_hours(self, start=22, end=8):
        if self._start_col is not None:
            return self[(self.start.dt.hour > start) | (self.end.dt.hour < end)]
        return self[(self.time.dt.hour > start) & (self.time.dt.hour < end)]

    def _select_at_day(self, day_or_class):
        if isinstance(day_or_class, pd.DataFrame):
            days = day_or_class.time.dt.date.unique()
            return self.time.dt.date.isin(days)
        elif isinstance(day_or_class, (list, tuple, set, pd.Series)):
            return self.time.dt.date.isin(set(day_or_class))
        else:
            mp = parse_date_tz(day_or_class)
            return (self.time.dt.date >= mp.start_date.date()) & (self.time.dt.date < mp.end_date.date())

    def at_day(self, day_or_class):
        return self[self._select_at_day(day_or_class)]

    def not_at_day(self, day_or_class):
        return self[~self._select_at_day(day_or_class)]

    @property
    def last_day(self):
        return self[(self.time > yesterday()) & (self.time < now())]

    @property
    def yesterday(self):
        return self[(self.time > yesterday()) & (self.time < now())]

    @property
    def last_week(self):
        return self[(self.time > last_week()) & (self.time < now())]

    @property
    def last_month(self):
        return self[(self.time > last_month()) & (self.time < now())]

    @property
    def last_year(self):
        return self[(self.time > last_year()) & (self.time < now())]

    @property
    def duration(self):
        return self.end - self.start

    @nlp("filter", "last", "last time", "most recently")
    def last(self):
        _ = self.time  # to get inferred time if not set
        col = self._time_col or self._start_col
        return self.__class__(self.sort_values(col, na_position="last", ascending=False).iloc[:1])


def now(**kwargs):
    return datetime.now(tz=tz) - relativedelta(**kwargs)


def last_days(days):
    return now(days=days).replace(hour=0, minute=0, second=0, microsecond=0)


def today():
    return last_days(0)


def yesterday():
    return last_days(1)


def last_week():
    return now(days=7).replace(hour=0, minute=0, second=0, microsecond=0)


def last_month():
    return now(months=1).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def last_year():
    return now(years=1).replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def week_ago(weeks):
    begin = now(days=7 * weeks).date()
    end = now(days=7 * (weeks - 1)).date()
    return begin, end


def days_ago(days):
    begin = now(days=days).date()
    end = now(days=days - 1).date()
    return lambda: (begin, end)


def months_ago(months):
    begin = now(months=months).date()
    end = now(months=months - 1).date()
    return lambda: (begin, end)


def years_ago(years):
    begin = now(years=years).date()
    end = now(years=years - 1).date()
    return lambda: (begin, end)


def in_month(month):
    year = now().year - 1 if now().month <= month else now().year
    return lambda: (datetime(year, month, 1).date(), datetime(year, month, 1).date() + relativedelta(month=month + 1),)


def in_year(year):
    return lambda: (datetime(year, 1, 1).date(), datetime(year + 1, 1, 1).date())


def try_date(x, min_level=None, max_level=None):
    try:
        # apparently one col is dayfirst, the other isnt
        mps = parse_date(x, multi=True)
        for mp in mps:
            if mp is None:
                continue
            if Units.DAY not in mp.levels:
                continue
            if min_level is not None and mp.min_level > min_level:  # above minute level
                continue
            if max_level is not None and mp.max_level < max_level:
                continue
            date = mp.start_date
            if date.tzinfo is None:
                date = tz.localize(date)
            return date
    except:
        return None


def parse_date_tz(text):
    mp = parse_date(text)
    if mp is not None:
        if mp.start_date.tzinfo is None:
            mp.start_date = tz.localize(mp.start_date)
        if mp.end_date.tzinfo is None:
            mp.end_date = tz.localize(mp.end_date)
        return mp


def datetime_tz(*args):
    return tz.localize(datetime(*args))


def datetime_from_timestamp(x, tzone=tz):
    # would be year 3000
    x = float(x)
    if x > 32503683600:
        x = x // 1000
    if isinstance(tzone, str):
        tzone = timezone(tzone)
    x = datetime.fromtimestamp(x, tz=tzone)
    if tzone != tz:
        x = x.astimezone(tz)
    return x


def datetime_from_any_format(date, in_utc=False):
    if isinstance(date, datetime):
        return date
    base = dateparser.parse(str(date))
    if in_utc:
        return utc.localize(base).astimezone(tz)
    else:
        return tz.localize(base)


def datetime_from_format(s, fmt, in_utc=False):
    base = datetime.strptime(s, fmt)
    if in_utc:
        return utc.localize(base).astimezone(tz)
    else:
        return tz.localize(base)
