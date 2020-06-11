# Twitter source

This source is currently fed by a Twitter takeout.
It expects the downloaded zip to be stored in `~/Downloads`.

Once you run this code, the data will be ingested and postprocessed, so it can
be further handled by Python:

```py
from nostalgia.sources.twitter import Twitter

Twitter.ingest()
```

The ZIP archive will be unpacked and the files be stored in
`~/nostalgia_data/input/twitter`.

Now, add the following lines to your `~/nostalgia_data/nostalgia_entry.py`:

```py
from nostalgia.sources.twitter.ad_engagements import AdEngagements
from nostalgia.sources.twitter.connected_application import ConnectedApplication
from nostalgia.sources.twitter.device_token import DeviceToken
from nostalgia.sources.twitter.dm import DirectMessage
from nostalgia.sources.twitter.email_changed import EmailChanged
from nostalgia.sources.twitter.ip_audit import IpAudit
from nostalgia.sources.twitter.tweet import Tweet

ads = AdEngagements.load()
apps = ConnectedApplication.load()
dms = DirectMessage.load()
emails = EmailChanged.load()
ips = IpAudit.load()
tokens = DeviceToken.load()
tweets = Tweet.load()
```

Now you can start a Nostalgia Timeline and inspect your Twitter activity.
Enjoy!