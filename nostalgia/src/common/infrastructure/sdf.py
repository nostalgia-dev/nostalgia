import os

import just
import numpy as np
import pandas as pd

import nostalgia
import nostalgia.anonymizer
from nostalgia.extracter import load_from_download
from nostalgia.file_caching import save_df, load_df
from nostalgia.nlp import nlp_registry, nlp, n, COLUMN_BLACKLIST, ResultInfo
from nostalgia.utils import get_token_set, normalize_name, view


########################################################################################################################
### TODO - JOIN SECTION
########################################################################################################################
def ab_overlap_cd(a, b, c, d):
    return ((a < d) & (b > c)) | ((b > c) & (d > a))


def ab_overlap_c(a, b, c):
    return a <= c <= b

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

########################################################################################################################
### TODO - REGISTRY SECTION
########################################################################################################################
registry = {}


def get_type_from_registry(tp):
    for key, value in registry.items():
        if key.endswith(tp):
            return value

########################################################################################################################
### TODO - TIME SECTION
########################################################################################################################
def time(x):
    return x.time


def col_contains_wrapper(word, col):
    def col_contains(x):
        return x.col_contains(word, col)

    return col_contains

########################################################################################################################
### TODO ---------------------------------------
########################################################################################################################


class SDF(pd.DataFrame):
    aspects = []
    categories = []
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
        if self.df_name != "results":
            # TODO add registry layer
            if self.df_name not in registry:
                registry[self.df_name] = self
            # if the new data is smaller than what is in the registry, do not overwrite the registry
            # TODO add merging of df
            elif len(data) > registry[self.df_name].shape[0]:
                registry[self.df_name] = self
        # TODO what is n?
        # ===============================
        # df analysis part
        # ===============================
        if n:
            self.analyze(C)


    def analyze(self, C):
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

    def __repr__(self):
        # if not self.anonymized:
        #     return super(SDF, self).__repr__()
        return super(SDF, self).__repr__()

    ####################################################################################################################
    ### TODO -- ETL SECTION
    ####################################################################################################################

    @classmethod
    def ingest(cls):
        load_from_download(vendor=cls.vendor, **cls.ingest_settings)

    @classmethod
    def load_df(cls, nrows):
        return load_df(cls.get_normalized_name(), nrows)

    @classmethod
    def save_df(cls, df, name=None):
        return save_df(df, name or cls.get_normalized_name())

    @classmethod
    def load(cls, nrows=None):
        df = cls.load_df(nrows)
        return cls(df)

    @classmethod
    def register(cls):
        return cls.load(nrows=5)

    @classmethod
    def get_normalized_name(cls):
        return normalize_name(cls.__name__)

    @property
    def df_name(self):
        name = normalize_name(self.__class__.__name__)
        if self.vendor is not None and not name.startswith(self.vendor):
            name = self.vendor + "_" + name
        return name

    @classmethod
    def class_df_name(cls):
        name = normalize_name(cls.__name__)
        if cls.vendor is not None and not name.startswith(cls.vendor):
            name = cls.vendor + "_" + name
        return name

    @classmethod
    def df_label(cls):
        return normalize_name(cls.__name__).replace("_", " ").title()

    @classmethod
    def get_schema(cls, *args, **kwargs):
        sample = cls.load(*args, nrows=5, **kwargs)
        return {k: v for k, v in zip(sample.columns, sample.dtypes)}

    def create_sample_data(self):
        nostalgia_dir = os.path.dirname(nostalgia.__file__)
        fname = os.path.join(nostalgia_dir, "data/samples/" + self.df_name + ".parquet")
        # verify that we can process it
        _ = self.as_simple()
        sample = self.iloc[:100].reset_index().drop("index", axis=1)
        # if self.is_anonymized:
        #     for x in self.anonymized:
        #         dtype = self.dtypes[x]
        #         if str(self.dtypes[x]) == "object":
        #             sample[x] = x
        #         else:
        #             sample[x] = np.random.choice(sample[x], sample.shape[0])
        #         assert sample[x].dtype == dtype
        n = min(sample.shape[0], 5)
        if n == 0:
            raise ValueError("Empty DataFrame, cannot make sample")
        sample = (
            sample.sample(n)
                .reset_index()
                .drop("index", axis=1)
                .drop("level_0", axis=1, errors="ignore")
        )
        sample.to_parquet(fname)
        print(f"Sample save as {os.path.abspath(fname)}")
        return sample

    @classmethod
    def load_sample_data(cls):
        nostalgia_dir = os.path.dirname(nostalgia.__file__)
        fname = os.path.join(nostalgia_dir, "data/samples/" + cls.class_df_name() + ".parquet")
        if os.path.exists(fname):
            print("loaded method 1")
            df = pd.read_parquet(fname)
        else:
            import pkgutil
            from io import BytesIO

            nostalgia_dir = os.path.dirname(nostalgia.__file__)
            sample_name = "data/samples/" + cls.class_df_name() + ".parquet"

            data = pkgutil.get_data("nostalgia", sample_name)
            print("loaded method 2")
            df = pd.read_parquet(BytesIO(data))
        return cls(df)

    def read(self, index):
        return just.read(self.path[index])

    def view(self, index):
        view(self.path[index])

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
            raise ValueError(f"No fields are mapped for {self.__class__.__name__}")

    def to_html(self):
        if self.selected_columns:
            data = pd.DataFrame({x: getattr(self, x) for x in self.selected_columns})
            return data.to_html()
        return super().to_html()

    ####################################################################################################################
    ### TODO -- UNCLASSIFIED
    ####################################################################################################################

    def take_from(self, registry_ending, col_name):
        for registry_type in registry:
            if not registry_type.endswith(registry_ending):
                continue
            # ODO: loop over columns, so we only do index lookup once
            # ODO: do not only try self.time but also self.end
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

    def containing(self, string, col_name=None, case=False, regex=True, na=False, bound=True):
        """
        Filters using string in all string columns when col_name is None, otherwise in just that one
        When `bound=True` it means to add word boundaries to the regex.
        case=True is whether to be case-sensitive
        regex=True means to treat string as regex
        na=False means to consider NaN to be considered False
        """
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

    @nlp("end", "how many", "how many times", "how often")
    def count(self):
        return self.shape[0]

    def sort_values(
        self, by, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last'
    ):
        return self.__class__(
            pd.DataFrame.sort_values(self, by, axis, ascending, inplace, kind, na_position)
        )

    # maybe which/what could be showing only unique?
    @nlp("end", "show", "show me", "show me the", "show the", "what")
    def show_me(self):
        _ = self.time  # to get inferred time if not set
        col = self._time_col or self._start_col
        return self.__class__(self.sort_values(col, na_position="last", ascending=False))

    @staticmethod
    def get_type_from_registry(tp):
        for key, value in registry.items():
            if key.endswith(tp):
                return value

    def __call_(self):
        return self



class Results(SDF):
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
