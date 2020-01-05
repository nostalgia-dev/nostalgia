from pytz import timezone
from pytz.reference import Local
from metadate import parse_date, Units
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import dateutil

# tz = timezone('Europe/Amsterdam')
tz = timezone(Local.tzname(datetime.now()))
utc = timezone('UTC')


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
    return lambda: (
        datetime(year, month, 1).date(),
        datetime(year, month, 1).date() + relativedelta(month=month + 1),
    )


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


def datetime_from_format(s, fmt, in_utc=False):
    base = datetime.strptime(s, fmt)
    if in_utc:
        return utc.localize(base).astimezone(tz)
    else:
        return tz.localize(base)
