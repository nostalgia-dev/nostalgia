Nostalgia DataFrames can be queried using pandas-like functionality. Look at the class for all available methods.

Note that `time` is automatically recognized in data. When there is only 1 datetime column, it is understood that it is a moment rather than a period.
It is important to understand that by default `nostalgia` tries to be smart about strings, datetime and metadate, especially since it can concern moments and periods.

Let's have a brief look at `metadate`:

```python
# On 6th of January 2020

from metadate import parse_date

mp = parse_date("yesterday")
# MetaPeriod(2020-01-05 00:00:00, 2020-01-06 00:00:00, {<Units.DAY: 4>}, ['yesterday'], en)
mp.start_date
# datetime.datetime(2020, 1, 5, 0, 0)

mp = parse_date("november 2019")
# MetaPeriod(2019-11-01 00:00:00, 2019-12-01 00:00:00,
            {<Units.YEAR: 9>, <Units.MONTH: 6>}, ['november', '2019'], en)
mp.start_date
# datetime.datetime(2019, 11, 1, 0, 0)

mp = parse_date("today at 1")
# MetaPeriod(2020-01-06 01:00:00, 2020-01-06 02:00:00, {<Units.HOUR: 3>, <Units.DAY: 4>}, ['today', 'at 1'], en)
```

You can see it has both a starting and ending date, and that it tries to be clever about finding the boundaries.
It understood we are interested at the hour level with "today at 1".

Keep in mind that start and end date are important when querying.

## Data

Let's consider the following example data:

```python
In[11]: from nostalgia.sources.chrome_history import WebHistory
web = WebHistory.load()
web.tail(n=2)

Out[11]:
              domain  domain_and_suffix                               time
98477      archlinux      archlinux.org   2019-12-23 01:23:38.429000+01:00
98478  stackoverflow  stackoverflow.com   2019-12-23 01:27:22.652000+01:00

                                                   title
98477  [BUG FILED] pyqt5-common removed from repos; u...
98478  Stack Overflow - Where Developers Learn, Share...

                                                     url
98477  https://bbs.archlinux.org/viewtopic.php?id=251356
98478                         https://stackoverflow.com/

                                                    path
98477  ~/nostalgia_data/html/1577060618.4289877_https...
98478  ~/nostalgia_data/html/1577060842.6447568_https...
```

## Time helpers

### Simple examples

In [7]: last_year()
Out[7]: datetime.datetime(2019, 1, 1, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

In [8]: last_month()
Out[8]: datetime.datetime(2019, 12, 1, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

In [11]: last_days(0)
Out[11]: datetime.datetime(2020, 1, 6, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

In [12]: last_days(1)
Out[12]: datetime.datetime(2020, 1, 5, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)
```

### ndf.last_year, ndf.last_month, ndf.last_day

```python
# On 6th of January 2020
web.last_year # returns all rows in 2019
web.last_month # returns all rows of december 2019
web.yesterday
```

This will filter the current data by `last_year`, in January 2020 that means the whole of 2019.

### ndf.at_time

This is the wrapper for allowing flexibility:

```python
def at_time(self, start, end=None, sort_diff=True, **window_kwargs):
```

If you give `start="yesterday"`
