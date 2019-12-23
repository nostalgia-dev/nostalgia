import inspect
from collections import defaultdict
from functools import wraps
from nostalgia.times import parse_date_tz

nlp_registry = defaultdict(set)
regex_registry = defaultdict(set)
ts = None

# from nearnlp import Near
# n = Near()
n = None


class ResultInfo(object):
    __slots__ = ('cls', 'role', 'cls_fn', 'col_name', 'orig_word')

    def __init__(self, cls, role, cls_fn=None, col_name=None, orig_word=None):
        self.cls = cls
        self.role = role
        self.cls_fn = cls_fn
        self.col_name = col_name
        self.orig_word = orig_word

    def repr_wrapper(self, x):
        v = None
        if x == "cls_fn":
            try:
                v = str(self.cls_fn).split()[1].split(".")[-1]
            except IndexError:
                pass
        if v is None:
            v = getattr(self, x)
        return v

    @property
    def tp(self):
        if isinstance(self.cls, str):
            return self.cls.split(".")[0]
        return self.cls.__name__

    def __repr__(self):
        try:
            c = getattr(self, "cls").__name__
        except AttributeError:
            c = getattr(self, "cls")
        return "!{}({})".format(
            c,
            ", ".join(
                ["{}={!r}".format(x, self.repr_wrapper(x)) for x in self.__slots__ if x != "cls"]
            ),
        )

    def __hash__(self):
        return hash((self.cls, self.col_name, self.orig_word))

    def __eq__(self, o):
        return (self.cls, self.col_name, self.orig_word) == (o.cls, o.col_name, o.orig_word)


COLUMN_BLACKLIST = set(["did", "was", "the", "a", "are", "i", "from", "hard", "for"])


def att_getter(fn):
    def att_inner(x, *args):
        try:
            return getattr(x, fn.__name__)(*args)
        except TypeError:
            return getattr(x, fn.__name__)()

    return att_inner


# has to be completed still
def regex(role, *keywords):
    def real_decorator(fn):
        for keyword in keywords:
            if isinstance(keyword, str):
                nlp_registry[keyword].add(
                    ResultInfo(fn.__qualname__, role, att_getter(fn), orig_word=keyword)
                )
            else:
                for kw in keyword:
                    nlp_registry[kw].add(
                        ResultInfo(fn.__qualname__, role, att_getter(fn), orig_word=kw)
                    )

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return real_decorator


def nlp(role, *keywords):
    def real_decorator(fn):
        # this does not work!!!!
        # is_prop = inspect.isdatadescriptor(fn)
        # defin = ", ".join([x for x in inspect.getfullargspec(fn).args if x != "self"])
        # if not is_prop:
        #     defin = "({})".format(defin)
        for keyword in keywords:
            if isinstance(keyword, str):
                nlp_registry[keyword].add(
                    ResultInfo(fn.__qualname__, role, att_getter(fn), orig_word=keyword)
                )
            else:
                for kw in keyword:
                    nlp_registry[kw].add(
                        ResultInfo(fn.__qualname__, role, att_getter(fn), orig_word=kw)
                    )

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return real_decorator


from textsearch import TextSearch


def get_ts():
    ts = TextSearch("insensitive", "object")
    ts.add(nlp_registry)
    return ts


def at_time_wrapper(mp):
    def at_time(x):
        return x.at_time(mp)

    return at_time


def find_entities(sentence):
    global ts
    if ts is None:
        ts = get_ts()
    mp = parse_date_tz(sentence)
    try:
        ents = ts.findall(sentence)
    except AttributeError:
        raise AttributeError("No entities have been registered")
    # remove metaperiod tokens from otherwise matching
    if mp is not None:
        wrongs = set()
        for l, e in mp.spans:
            wrongs.update(range(l, e))
        ents = [x for x in ents if x.start not in wrongs and x.end not in wrongs]
        ents.append(ResultInfo("MP", "filter", at_time_wrapper(mp), orig_word=" ".join(mp.matches)))
    return ents
