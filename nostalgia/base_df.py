import os
import re
import pandas as pd
import numpy as np
from nostalgia.utils import now, yesterday, last_week, last_month, last_year, parse_date_tz, view
from metadate import is_mp
from datetime import timedelta
import just
from nostalgia.nlp import nlp_registry, nlp, n, COLUMN_BLACKLIST, ResultInfo
from nostalgia.utils import get_token_set, normalize_name
from nostalgia.source_to_fast import get_newline_count, save_newline_count
from nostalgia.source_to_fast import get_processed_files, save_processed_files
from nostalgia.source_to_fast import get_last_latest_file, save_last_latest_file
from nostalgia.source_to_fast import get_last_mod_time, save_last_mod_time
from nostalgia.source_to_fast import save, load
from nostalgia.utils import read_array_of_dict_from_json


def ab_overlap_cd(a, b, c, d):
    return ((a < d) & (b > c)) | ((b > c) & (d > a))


def ab_overlap_c(a, b, c):
    return (a <= c) & (c <= b)


def join_time_naive(locs, df, **window_kwargs):
    tmp = []
    if not locs.inferred_time:
        locs.infer_time()
    for _, row in locs.iterrows():
        if df.start is not None:
            if locs._start_col is None:
                start = row[locs._time_col] - pd.Timedelta(**window_kwargs)
                end = row[locs._time_col] + pd.Timedelta(**window_kwargs)
            else:
                start = row[locs._start_col]
                end = row[locs._end_col]
            res = df[ab_overlap_cd(df.start, df.end, start, end)]
        else:
            if locs._start_col is None:
                start = row[locs._time_col] - pd.Timedelta(**window_kwargs)
                end = row[locs._time_col] + pd.Timedelta(**window_kwargs)
            else:
                start, end = row.start, row.end
            res = df[df.time.between(start, end)]
        if not res.empty:
            # import pdb
            # pdb.set_trace()
            tmp.append(res)
    if not tmp:
        return df[:0]
    tmp = pd.concat([pd.DataFrame(x) for x in tmp])
    try:
        tmp = tmp.drop_duplicates()
    except TypeError:
        tmp = tmp[~tmp.astype(str).duplicated()]
    return tmp


def join_time_index(locs, df, **window_kwargs):
    try:
        return df[df.time.apply(lambda x: locs.index.contains(x))]
    except TypeError:
        print("warning")
        return join_time_naive(locs, df, **window_kwargs)


def join_time(locs, df, **window_kwargs):
    if df.start is not None:
        return join_time_naive(locs, df, **window_kwargs)
    if not str(df.index.dtype).startswith("interval"):
        return join_time_naive(locs, df, **window_kwargs)
    W = locs.shape[0]
    L = df.shape[0]
    y = 0.001 + W * -0.318 + L * 0.013
    if y > 300:
        p = 1
    else:
        exponent = np.exp(y)
        p = exponent / (1 + exponent)
    if p > 0.5:
        fn = join_time_naive
    else:
        fn = join_time_index
    return fn(locs, df, **window_kwargs)


registry = {}


def get_type_from_registry(tp):
    for key, value in registry.items():
        if key.endswith(tp):
            return value


def time(x):
    return x.time


def col_contains_wrapper(word, col):
    def col_contains(x):
        return x.col_contains(word, col)

    return col_contains


class DF(pd.DataFrame):
    keywords = []
    nlp_columns = []
    nlp_when = True
    selected_columns = []
    vendor = None

    def __init__(self, data):
        super().__init__(data)
        C = self.__class__
        self.num_times = None
        self._start_col, self._time_col, self._end_col = None, None, None
        self.inferred_time = False
        # IF BIG BREAK, THEN THIS IS HERE
        # if self.df_name not in registry:
        #     registry[self.df_name] = self
        if self.df_name != "result":
            if self.df_name not in registry:
                registry[self.df_name] = self
            # if the new data is smaller than what is in the registry, do not overwrite the registry
            elif data.shape[0] > registry[self.df_name].shape[0]:
                registry[self.df_name] = self
        if n is None:
            return
        seen_keyword_keywords = set()
        for kw in self.keywords:
            for w in n.simple_extend(kw):
                if w and isinstance(w, str):
                    nlp_registry[w].add(ResultInfo(C, "start", orig_word=kw))
                    seen_keyword_keywords.add(w)
            nlp_registry[kw].add(ResultInfo(C, "start", orig_word=kw))
            seen_keyword_keywords.add(kw)
        # nlp_keywords_column = []
        # if "keywords" in data:
        #     nlp_keywords_column = ["keywords"]
        BLACKLIST = seen_keyword_keywords.union(COLUMN_BLACKLIST)
        for col in self.nlp_columns:
            words = get_token_set(self[col].unique())
            for word in words:
                if word in BLACKLIST:
                    continue
                for w in n.simple_extend(word):
                    if w in BLACKLIST:
                        continue
                    if w and isinstance(w, str):
                        nlp_registry[w].add(
                            ResultInfo(C, "filter", col_contains_wrapper(word, col), col, word)
                        )
                if n.is_verb(word):
                    for w in n.get_verbs(word).values():
                        if w in BLACKLIST:
                            continue
                        if w in words or not isinstance(w, str):
                            continue
                        nlp_registry[w].add(
                            ResultInfo(C, "filter", col_contains_wrapper(word, col), col, word)
                        )
                if n.is_verb(word):
                    for w in n.get_verbs(word).values():
                        if w in BLACKLIST:
                            continue
                        if w in words or not isinstance(w, str):
                            continue
                        nlp_registry[w].add(
                            ResultInfo(C, "filter", col_contains_wrapper(word, col), col, word)
                        )
                nlp_registry[word].add(
                    ResultInfo(C, "filter", col_contains_wrapper(word, col), col, word)
                )
        if self.nlp_when:
            nlp_registry["when"].add(ResultInfo(C, "end", time, orig_word="when"))

    @property
    def df_name(self):
        name = normalize_name(self.__class__.__name__)
        if self.vendor is not None:
            name = self.vendor + "_" + name
        return name

    @classmethod
    def df_label(cls):
        return normalize_name(cls.__name__).replace("_", " ").title()

    @classmethod
    def load_data_file_modified_time(cls, fname, key_name="", nrows=None, from_cache=True):
        name = fname + "_" + normalize_name(cls.__name__)
        modified_time = os.path.getmtime(os.path.expanduser(fname))
        last_modified = get_last_mod_time(name)
        if modified_time != last_modified or not from_cache:
            if fname.endswith(".csv"):
                data = pd.read_csv(fname, error_bad_lines=False, nrows=nrows)
            else:
                data = read_array_of_dict_from_json(fname, key_name, nrows)
            data = cls.handle_dataframe_per_file(data, fname)
            if nrows is None:
                save(data, name)
                save_last_mod_time(modified_time, name)
        else:
            data = load(name)
        return data

    @classmethod
    def load_dataframe_per_json_file(cls, glob_pattern, key="", nrows=None):
        fnames = set(just.glob(glob_pattern))
        name = glob_pattern + "_" + normalize_name(cls.__name__)
        processed_files = get_processed_files(name)
        to_process = fnames.difference(processed_files)
        objects = []
        if nrows is not None:
            if not to_process:
                to_process = list(processed_files)[-1:]
            else:
                to_process = list(to_process)[-1:]
        if to_process:
            for fname in to_process:
                data = read_array_of_dict_from_json(fname, key, nrows)
                data = cls.handle_dataframe_per_file(data, fname)
                if data is None:
                    continue
                objects.append(data)
            data = pd.concat(objects)
            if processed_files and nrows is None:
                data = pd.concat((data, load(name)))
            for x in ["time", "start", "end"]:
                if x in data:
                    data = data.sort_values(x)
                    break
            if nrows is None:
                save(data, name)
                save_processed_files(fnames | processed_files, name)
        else:
            data = load(name)
        return data

    @classmethod
    def load_object_per_newline(cls, fname, nrows=None):
        data = []
        name = fname + "_" + normalize_name(cls.__name__)
        newline_count = get_newline_count(name)
        for i, x in enumerate(just.iread(fname)):
            if nrows is None:
                if i < newline_count:
                    continue
            row = cls.object_to_row(x)
            if row is None:
                continue
            data.append(row)
            # breaking at approx 5 rows
            if nrows is not None and i > nrows:
                break
        if data:
            data = pd.DataFrame(data)
            if newline_count and nrows is None:
                data = pd.concat((data, load(name)))
            for x in ["time", "start", "end"]:
                if x in data:
                    data = data.sort_values(x)
                    break
            if nrows is None:
                save(data, name)
                n = i + 1
                save_newline_count(n, name)
        else:
            data = load(name)
        return data

    @classmethod
    def latest_file_is_historic(cls, glob, key_name="", nrows=None, from_cache=True):
        recent = max([x for x in just.glob(glob) if "(" not in x], key=os.path.getctime)
        return cls.load_data_file_modified_time(recent, key_name, nrows, from_cache)

    @property
    def time(self):
        if not self.inferred_time:
            self.infer_time()
            self.inferred_time = True
        if self._time_col == "time":
            return self._get_item_cache(self._time_col)
        if self._time_col not in self:
            return None
        return getattr(self, self._time_col)

    # @property
    # def _constructor(self):
    #     return self.__class__

    def duration_longer_than(self, **timedelta_kwargs):
        return self[(self.end - self.time) >= timedelta(**timedelta_kwargs)]

    def duration_shorter_than(self, **timedelta_kwargs):
        return self[(self.end - self.time) <= timedelta(**timedelta_kwargs)]

    def take_from(self, registry_ending, col_name):
        for registry_type in registry:
            if not registry_type.endswith(registry_ending):
                continue
            # TODO: loop over columns, so we only do index lookup once
            # TODO: do not only try self.time but also self.end
            new_name = registry_ending + "_" + col_name
            if new_name in self.columns:
                return self[new_name]
            tp = get_type_from_registry(registry_type)
            results = []
            if not self.inferred_time:
                self.infer_time()
            for x in self[self._time_col]:
                try:
                    res = tp.loc[x]
                    if not isinstance(res, pd.Series):
                        res = res.iloc[0]
                    res = res[col_name]
                except (KeyError, TypeError):
                    res = np.nan
                results.append(res)
            self[new_name] = results
            return self[new_name]

    def add_heartrate(self):
        return self.take_from("heartrate", "value")

    def heartrate_range(self, low, high=None):
        if "heartrate_value" not in self.columns:
            self.add_heartrate()
        if high is not None and low is not None:
            return self[(self["heartrate_value"] >= low) & self["heartrate_value"] < high]
        if low is not None:
            return self[self["heartrate_value"] >= low]
        if high is not None:
            return self[self["heartrate_value"] < high]

    def heartrate_above(self, value):
        return self.heartrate_range(value)

    def heartrate_below(self, value):
        return self.heartrate_range(None, value)

    @classmethod
    def get_schema(cls, *args, **kwargs):
        sample = cls.load(*args, nrows=5, **kwargs)
        return {k: v for k, v in zip(sample.columns, sample.dtypes)}

    @property
    def start(self):
        if not self.inferred_time:
            self.infer_time()
            self.inferred_time = True
        if self._start_col == "start":
            return self._get_item_cache(self._start_col)
        if self._start_col not in self:
            return None
        return getattr(self, self._start_col)

    @property
    def _office_days(self):
        return self.time.dt.weekday < 5

    @property
    def _office_hours(self):
        if (self.time.dt.hour == 0).all():
            raise ValueError("Hours are not set, thus unreliable. Use `office_days` instead?")
        if self.start is not None:
            return np.array(
                [
                    (x >= 8 and x <= 17 and y >= 8 and y <= 17)
                    for x, y in zip(self.start.dt.hour, self.end.dt.hour)
                ]
            )
        return np.array([(x >= 8 and x <= 17) for x in self.time.dt.hour])

    @property
    def in_office_days(self):
        return self[self._office_days]

    @property
    def in_office_hours(self):
        return self[self._office_hours]

    @property
    def during_office_hours(self):
        return self[self._office_hours & self._office_days]

    @property
    def end(self):
        if not self.inferred_time:
            self.infer_time()
            self.inferred_time = True
        if self._end_col == "end":
            return self._get_item_cache(self._end_col)
        if self._end_col not in self:
            return None
        return getattr(self, self._end_col)

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

    def infer_time(self):
        times = [x for x, y in zip(self.columns, self.dtypes) if "datetime" in str(y)]
        levels = [self.time_level(self[x]) for x in times]
        max_level = max(levels)
        # workaround
        # start: 10:00:00
        # end:   10:00:59
        times = [t for t, l in zip(times, levels) if l == max_level or (l == 2 and max_level == 3)]
        num_times = len(times)
        self.num_times = num_times
        if num_times == 0:
            self._start_col, self._time_col, self._end_col = None, None, None
        elif num_times == 1:
            self._start_col, self._time_col, self._end_col = None, times[0], None
        elif num_times == 2:
            col1, col2 = times
            sub = self[self[col1].notnull() & self[col2].notnull()]
            a, b = sub[col1], sub[col2]
            if (a > b).all():
                col1, col2 = col2, col1
            elif not (a <= b).all():
                raise ValueError(
                    "Not strictly one col higher than other with dates, can't determine"
                )
            if col1 == "end" and col2 == "start":
                col2, col1 = col1, col2
            self._start_col, self._time_col, self._end_col = col1, col1, col2
        else:
            msg = 'infer time failed: there can only be 1 or 2 datetime columns at the same granularity.'

            raise Exception(msg + " Found: " + str(times))

    def when_at(self, other, **window_kwargs):
        if isinstance(other, str):
            other = get_type_from_registry("places").containing(other)
        return self.__class__(join_time(other, self, **window_kwargs))

    def browsing(self, other, **window_kwargs):
        if isinstance(other, str):
            other = get_type_from_registry("browser").containing(other)
        return self.__class__(join_time(other, self, **window_kwargs))

    def at_night(self, start=22, end=8):
        if self._start_col is not None:
            return self[(self.start.dt.hour > start) | (self.end.dt.hour < end)]
        return self[(self.time.dt.hour > start) | (self.time.dt.hour < end)]

    @property
    def when_asleep(self):
        return self.__class__(join_time(registry["sleep"], self))

        # browser["session"] = browser.time.diff().apply(lambda x: x.seconds > 20 * 60).cumsum()+10
        # session, start, end = zip(*[(name, group.iloc[0].time - pd.Timedelta(minutes=10), group.iloc[-1].time + pd.Timedelta(minutes=10)) for name, group in browser.groupby("session")])
        # df = pd.DataFrame({"session": session}, index=pd.IntervalIndex.from_arrays(start, end))
        # df.index.get_loc(pd.Timestamp(parse_date_tz("2019-09-18 18:40:56.729633").start_date))

    def col_contains(self, string, col_name, case=False, regex=False, na=False):
        return self[self[col_name].str.contains(string, case=case, regex=regex, na=na)]

    def __getitem__(self, key):
        new = super().__getitem__(key)
        if isinstance(new, pd.DataFrame):
            new = self.__class__(new)
        return new

    @property
    def text_cols(self):
        return [x for x, t in zip(self.columns, self.dtypes) if t == np.dtype('O')]

    @nlp("filter", "by me", "i", "my")
    def by_me(self):
        return self

    def containing(self, string, col_name=None, case=False, regex=True, na=False, bound=True):
        if regex and bound:
            string = r"\b" + string + r"\b"
        if col_name is not None:
            return self.col_contains(string, col_name, case, regex, na)
        bool_cols = [
            self[x].str.contains(string, case=case, regex=regex, na=na) for x in self.text_cols
        ]
        bool_array = bool_cols[0]
        for b in bool_cols[1:]:
            bool_array = np.logical_or(bool_array, b)
        return self.__class__(self[bool_array])

    def query(self, expr):
        return self.__class__(super().query(expr))

    def as_simple(self, max_n=None):
        data = {
            "title": self.df_name,  # default, to be overwritten
            "url": None,
            "start": None,
            "end": None,
            # "body": None,
            "type": self.df_name,
            "interval": True,
            "sender": None,
            "value": getattr(self, "value", None),
            "index_loc": self.index,
        }
        for x in ["title", "name", "naam", "subject", "url", "content", "text", "value"]:
            res = getattr(self, x, None)
            if res is not None:
                data["title"] = res
                break
        res = getattr(self, "sender", None)
        if res is not None:
            data["sender"] = res
        for x in ["url", "path", "file"]:
            res = getattr(self, x, None)
            if res is not None:
                data["url"] = res
                break
        for x in ["start", "time", "timestamp"]:
            res = getattr(self, x, None)
            if res is not None:
                data["start"] = res
                break
        for x in ["end"]:
            res = getattr(self, x, None)
            if res is not None:
                data["end"] = res - pd.Timedelta(microseconds=1)
                break
        if data["end"] is None:
            data["end"] = data["start"] + pd.Timedelta(minutes=5)
            data["interval"] = False
        try:
            data = pd.DataFrame(data).sort_values("start")
            if max_n is not None:
                data = data.iloc[-max_n:]
            return data
        except ValueError:
            raise ValueError("No fields are mapped")

    def at_day(self, day_or_class):
        if isinstance(day_or_class, pd.DataFrame):
            days = day_or_class.time.dt.date.unique()
            return self[self.time.dt.date.isin(days)]
        else:
            mp = parse_date_tz(day)
            return self[
                (self.time.dt.date >= mp.start_date.date())
                & (self.time.dt.date < mp.end_date.date())
            ]

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

    def near(self, s):
        if isinstance(s, DF) and s.df_name.endswith("places"):
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

    def read(self, index):
        return just.read(self.path[index])

    def view(self, index):
        view(self.path[index])

    def head(self, *args, **kwargs):
        return self.__class__(super().head(*args, **kwargs))

    def tail(self, *args, **kwargs):
        return self.__class__(super().tail(*args, **kwargs))

    @nlp("end", "how many", "how many times", "how often")
    def count(self):
        return self.shape[0]

    @property
    def at_home(self):
        self.take_from("places", "category")
        return self[self["places_category"] == "Home"]

    @property
    def at_work(self):
        self.take_from("places", "category")
        return self[self["places_category"] == "Work"]

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
            end = mp.start_date
        elif end is None and window_kwargs:
            end = start
        elif end is None:
            raise ValueError(
                "Either a metaperiod, a date string, 2 times, or time + window_kwargs."
            )
        self.infer_time()
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
            res = res.sort_values('sort_score').drop('sort_score', axis=1)
        return self.__class__(res)

    when = when_at

    @property
    def duration(self):
        return self.end - self.start

    def sort_values(
        self, by, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last'
    ):
        return self.__class__(
            pd.DataFrame.sort_values(self, by, axis, ascending, inplace, kind, na_position)
        )

    @nlp("filter", "last", "last time", "most recently")
    def last(self):
        _ = self.time  # to get inferred time if not set
        col = self._time_col or self._start_col
        return self.__class__(self.sort_values(col, na_position="last", ascending=False).iloc[:1])

    # maybe which/what could be showing only unique?
    @nlp("end", "show", "show me", "show me the", "show the", "what")
    def show_me(self):
        _ = self.time  # to get inferred time if not set
        col = self._time_col or self._start_col
        return self.__class__(self.sort_values(col, na_position="last", ascending=False))

    def at(self, time_or_place):
        if isinstance(time_or_place, DF) and time_or_place.df_name.endswith("places"):
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

    def to_html(self):
        if self.selected_columns:
            data = pd.DataFrame({x: getattr(self, x) for x in self.selected_columns})
            return data.to_html()
        return super().to_html()

    def get_type_from_registry(self, tp):
        for key, value in rergistry.items():
            if key.endswith(tp):
                return value

    def __call_(self):
        return self


# ov = ab_overlap_cd(
#     places.start,
#     places.end,
#     parse("2015-02-05 21:53:09.581001+00:00"),
#     parse("2015-02-05 21:53:13.881000+00:00"),
# )


class Results(DF):
    @classmethod
    def merge(cls, *dfs, max_n=None):
        data = pd.concat([x.as_simple(max_n) for x in dfs])
        data = data.set_index("start")
        data = data.sort_values("start", na_position="first")
        data["start"] = data.index
        return Results(data)

    def get_original(self, index_loc):
        row = self.iloc[index_loc]
        rec = registry[row.type].loc[row["index_loc"]]
        # rec.add_heartrate() # not here, but at the results level.. but then just to display
        # if a certain value
        if not isinstance(rec, pd.Series):
            rec = rec.iloc[0]
        return rec
