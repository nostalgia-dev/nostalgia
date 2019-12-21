# Samsung Health

Currently stress, heart rate and sleep are having bindings.

## Getting the data

The most complete way to get the data is via export (see [this article](https://www.dcrainmaker.com/2019/03/export-data-samsung-watch-galaxy-health-app.html) for other methods to extract personal data, though that are NOT supported in nostalgia).

### Android

1. Open the [Samsung Health] app and click on the Settings Icon. Then click on the Cog icon. Scroll all the way down and hit "Download personal data" and again "Download". Fill in your account details and the security code.

1. To transfer this data to your PC you can package it first as a .ZIP file. This assumes you have `AndroZip` installed.

1. Open it, and go to SD card. Click `Android`, then `Data`, then look for `com.sec.android.app.shealth`, then `files`, then `Download`

1. Long press folder that was created at the previous step and select Create Zip.

1. After it has been created, long press the zip file and click `Send To`. Then send it as an email to yourself.

1. On your PC download the zip file.

1. Open a Python interpreter:

```python
from nostalgia.sources.samsung import Samsung
Samsung.ingest()
```

This will load all the Samsung data from your download folder into the nostalgia source folder.

To verify you have the data available:

```python
from nostalgia.sources.samsung.heartrate import SamsungHeartrate
heartrate = SamsungHeartrate.load()
heartrate
                                            heart_rate_max  ...  value
(2019-11-25 12:44:00, 2019-11-25 12:44:59]              70  ...     70
(2019-11-25 12:45:00, 2019-11-25 12:45:59]              92  ...     90
(2019-11-25 12:46:00, 2019-11-25 12:46:59]             104  ...     98
```
