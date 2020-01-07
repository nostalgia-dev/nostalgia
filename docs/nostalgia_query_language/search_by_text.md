Nostalgia DataFrames can be queried using pandas-like functionality. Look at the class for all available methods.

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

### ndf.containing

It is possible to query all the string columns at once (when `col_name=None`, searches all `object` type columns).

```def containing(string, col_name=None, case=False, regex=True, na=False, bound=True):```

For each row, if any of those columns contain the string it will be returned. It takes the `regex` and `case` arguments to allow it to be interpreted as a regex, and whether to be case-sensitive.

When `bound=True` it means to add word boundaries (`"\b"`) to the regex on both sides.

The following will return rows in which any of the text columns contains `"sweet"` as a word, but not `"sweettooth"` since `bound=True`.

```python
web.containing("sweet")
```

### ndf.query

A wrapper around pandas df.query: use expressions to filter and return a subselection, e.g.:

```python
web.query("url == 'https://github.com/nostalgia-dev'")
```
