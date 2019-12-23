# Google Takeout

It allows you to all personal data from Google by using an export.

## Getting the data

It is possible to grab your data here: [https://takeout.google.com/](https://takeout.google.com/). Ensure to select JSON whenever given the option.

Note that it can take days to complete in case you are grabbing everything. I mostly noticed it is slow for images and email. If you for example only select **My Activity** (which contains a lot already) and perhaps some other not small categories, you can easily test it out.

### Android

1. After the export is completed, download the zip file. It assumes your downloads end up in `~/Downloads`

1. Open a Python interpreter:

```python
from nostalgia.sources.google import Google
Google.ingest()
```

This will load all the Google from your download folder into the nostalgia source folder (`~/nostalgia_data/input/google/`).

To verify you have the data available, try for example one of the following (depending on what you've exported):

#### Android App Usage

```python
from nostalgia.sources.google.app_usage import AppUsage
apps = AppUsage.load()
apps
                                                  name                             time
0                                              Android        2019-12-20 09:00:00+01:00
1                                       Pixel Launcher 2019-12-20 08:37:32.384000+01:00
2      Sleep Cycle: Sleep analysis & Smart alarm clock 2019-12-20 08:37:29.517000+01:00
```

#### Page Visit

```python
from nostalgia.sources.google.page_visit import AppUsage
pages = AppUsage.load()
pages
>>> PageVisit.load()
          ...                                                url                             time
0         ...        https://takeout.google.com/settings/takeout 2019-12-17 15:29:25.041000+01:00
1         ...        https://takeout.google.com/settings/takeout 2019-12-17 15:29:23.744000+01:00
```
