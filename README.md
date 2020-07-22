<p align="center">
  <img src="https://nostalgia-dev.github.io/assets/images/biglogo.png" width="200px" alt="nostalgia"/>
</p>

[![PyPI][shields]][pypi]
[![PyPI][shields-pyversion]][pypi]

### Ecosystem for combining personal data

Nostalgia will help with gathering data from a variety of sources and enable you to combine them easily.

It's much like [Home Assistant][home_assistant], providing a platform, but then for connecting data instead of IoT devices.

Afterwards, it will help you filter and visualize the data.

The architecture is as follows. You're looking at the core which contains the code for ingesting sources, installing the backend system and allows you to write scripts using Nostalgia Query Language.

If you want to add your own data that is not supported, please for now contact us directly in either [discord][discord] or [slack][slack] and we'll help you get started. You can also look at the [open issues][issues] to see suggestions for new sources.

### Available Data Bindings

Full list of current [sources][sources].

- Heartrate ([Fitbit][fitbit], [Samsung Watch][samsung])
- Sleep ([Fitbit][fitbit_sleep], [Samsung Watch][samsung], SleepCycle)
- Places (Google Timeline)
- Bank Payments (ING)
- Pictures ([Google Photos][picasa])
- Emails ([Gmail][gmail], [Others (IMAP based)][imap])
- App Usage ([Android][android])
- Calendar ([Google][calendar])
- Chat Conversations ([WhatsApp][whatsapp], [Facebook Messages][facebook])
- Music listening ([Google Play Music][music])
- Music identification ([Shazam][shazam])
- Posts ([Reddit][reddit], [Facebook][facebook], [Twitter][twitter])
- File Visits ([Emacs][emacs])
- Annotated Screenshots (Tesseract)
- Web ([Nostalgia Chrome Plugin][chrome]) - works in Opera, Firefox, Brave, too!
  - Products
  - Events
  - Videos
  - Google Search
  - People
- Indoor Positioning ([whereami][whereami])
- Public Transport (MijnOV)

### Getting started

1. If you're a user: `pip install nostalgia` or... `pip install -e .` if you might want to develop on Nostalgia

1. Follow the instructions for a [source of interest][data_bindings] to ensure it is loaded

1. Use the data in an interactive session (run Python) OR [run the timeline][timeline]

1. To upgrade Nostalgia, as user run `pip install -U nostalgia` or as developer run `git pull`.

### Nostalgia Query Language - extending pandas

Given that you have payments, heartrate and google places set up, you could start Python and run:

```python
In [15]: from nostalgia.sources.ing_banking.mijn_ing import Payments

payments = Payments.load()

payments.by_card\
        .last_year\
        .in_office_days\
        .during_hours(7, 12)\
        .by_me()\
        .heartrate_above(100)\
        .when_at("amsterdam")\
        .sum()

Out[15]: 7.65 # in euros
```

This will give the total expenses by card in the last week, but only on work days, at night, when my heart rate is above 80 and I'm in Amsterdam.
It combined the generic class functionality, together with data from:

- A Payments provider
- A Location provider
- A Heartrate provider

### Contributing

Please contribute the data sources that others could use as well!

[android]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/app_usage.py
[calendar]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/calendar.py
[chrome]: https://github.com/nostalgia-dev/nostalgia_chrome
[data_bindings]: #available-data-bindings
[discord]: https://discord.gg/nJQfM2A
[emacs]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/emacs_file_visits.py
[facebook]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/facebook/messages.py
[fitbit]: https://github.com/nostalgia-dev/nostalgia_fitbit
[fitbit_sleep]: https://github.com/kootenpv/nostalgia_fitbit
[gmail]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/gmail.py
[imap]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/email/__init__.py
[home_assistant]: https://github.com/home-assistant/home-assistant
[issues]: https://github.com/nostalgia-dev/nostalgia/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc
[music]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/play_music.py
[picasa]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/photos.py
[pypi]: https://pypi.python.org/pypi/nostalgia/
[reddit]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/reddit_posts.py
[samsung]: https://github.com/nostalgia-dev/nostalgia/blob/master/nostalgia/sources/samsung/README.md
[shazam]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/shazam.py
[shields]: https://img.shields.io/pypi/v/nostalgia.svg?style=flat-square
[shields-pyversion]: https://img.shields.io/pypi/pyversions/nostalgia.svg?style=flat-square
[slack]: https://bit.ly/2Yre09N
[sources]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources
[timeline]: https://github.com/nostalgia-dev/timeline
[twitter]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/twitter/tweet.py
[whatsapp]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/whatsapp.py
[whereami]: https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/whereami/scheduler.py
