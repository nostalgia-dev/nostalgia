# Connect Your Data

Each source has specific instructions on how to get the data into the ecosystem.

The benefit of the system starts to show the more data is connected and can be searched/utilized at once.

There are 3 ways to find data to connect: **searching**, **data type overview** and **vendor overview**. The latter 2 can also help you *discover/inspire* you to connect other data.

## Searching

In case you are looking for a particular source, you can [search on github](https://github.com/nostalgia-dev/nostalgia/search?utf8=%E2%9C%93&q=gmail&type=), or goto [the documentation](https://nostalgia-dev.github.io/nostalgia/) and search.

## Data type overview

- Heartrate ([Fitbit](https://github.com/kootenpv/nostalgia_fitbit), [Samsung Watch](https://github.com/nostalgia-dev/nostalgia/blob/master/nostalgia/sources/samsung/README.md))
- Sleep ([Fitbit](https://github.com/kootenpv/nostalgia_fitbit), [Samsung Watch](https://github.com/nostalgia-dev/nostalgia/blob/master/nostalgia/sources/samsung/README.md), SleepCycle)
- Places (Google Timeline)
- Bank Payments (ING)
- Pictures ([Google]((https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/photos.py)))
- Emails ([Gmail]((https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/gmail.py)))
- App Usage ([Google/Android]((https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/app_usage.py)))
- Chat Conversations ([WhatsApp](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/whatsapp.py), [Facebook Messenger](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/facebook/messages.py))
- Music listening ([Google](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google/play_music.py))
- Music identification ([Shazam](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/shazam.py))
- Posts ([Reddit](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/reddit_posts.py), Facebook)
- File Visits ([Emacs](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/emacs_file_visits.py))
- Annotated Screenshots (Tesseract)
- Web ([Nostalgia Chrome Plugin](https://github.com/nostalgia-dev/nostalgia_chrome))
  - Products
  - Events
  - Videos
  - Google Search
  - People
- Indoor Positioning ([whereami](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/whereami/scheduler.py))
- Public Transport (MijnOV)

## Vendor overview

If you're looking to load in a lot of data at once, consider adding data from these vendors:

- [Facebook](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/facebook)
- [Google](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/google)
- [Samsung Health (watch)](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/samsung)
- [Chrome History](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/web)
- [Fitbit](https://github.com/nostalgia-dev/nostalgia/tree/master/nostalgia/sources/fitbit)

## Data missing?

In case the data you want to connect is not in here, you can add it yourself (and please consider contributing it to the ecosystem!).
