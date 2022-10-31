import just
import pandas as pd
from nostalgia.interfaces.chat import ChatInterface
from nostalgia.times import datetime_from_format, parse_datetime, tz

offset = len("01/10/2019, 20:02 - ")

from datetime import datetime


class WhatsappChat(ChatInterface):
    """# WhatsApp Chat
     WhatsApp allows you to export a single conversation (.txt) by email using a mobile app. Below official instructions for each platform:

     - [Android](https://faq.whatsapp.com/en/android/23756533/)
     - iPhone (does not work)
     - [Windows Phone](https://faq.whatsapp.com/en/wp/22548236)

    ### Other method

     datas = []
     for fname in just.glob("~/Downloads/*.csv"):
         try:
             with open(fname) as f:
                 chars = f.read(30)
                 if "Date1;Date2;Time;UserPhone" not in chars:
                     continue
                 datas.append(pd.read_csv(fname, sep=";"))
         except PermissionError:
             continue

    ### Create instance
    Click below on the `+` sign and fill in the path to the WhatsApp chat file."""

    vendor = "whatsapp"
    me = "Pascal"
    sender_column = "sender"

    @classmethod
    def load(cls, nrows=None, **kwargs):
        old_text = ""
        results = []
        nrows = nrows or 50_000_000_000
        for file_path in just.glob("~/nostalgia_data/input/whatsapp/*.txt"):
            row = 0
            for line in just.iread(file_path):
                try:
                    time = datetime_from_format(line[:offset], "%d/%m/%Y, %H:%M - ")
                except ValueError:
                    old_text += line + "\n"
                    continue
                line = old_text + line[offset:]
                old_text = ""
                try:
                    if line.startswith("Messages to this chat and calls are now secured"):
                        continue
                    sender, text = line.split(": ", 1)
                except ValueError:
                    print("ERR", line)
                    continue
                if line:
                    if row > nrows:
                        break
                    row += 1
                    results.append((time, sender, text))
        for x in just.glob("~/Downloads/*.csv"):
            tmp_cols = pd.read_csv(x, nrows=1, sep=";").columns
            if all([c in tmp_cols for c in ["Date2", "Time", "UserName", "MessageBody"]]):
                just.rename(x, "~/nostalgia_data/input/whatsapp/" + x.split("/")[-1])

        tz_str = None
        for file_path in just.glob("~/nostalgia_data/input/whatsapp/*.csv"):
            df = pd.read_csv(file_path, sep=";", nrows=nrows)
            if tz_str is None:
                d, t = df.Date2.iloc[0], df.Time.iloc[0]
                tz_str = parse_datetime(d + "T" + t).replace(tzinfo=tz).isoformat()[-6:]
            results.extend(
                [
                    (parse_datetime(f"{d}T{t}{tz_str}"), u, m)
                    for d, t, u, m in zip(df.Date2, df.Time, df.UserName, df.MessageBody)
                ]
            )
        df = pd.DataFrame(results, columns=["time", "sender", "text"])
        # hack "order" into minute data
        same_minute = df.time == df.shift(1).time
        seconds = []
        second_prop = 0
        for x in same_minute:
            if x:
                second_prop += 1
            else:
                second_prop = 0
            seconds.append(pd.Timedelta(seconds=60 * second_prop / (second_prop + 1)))
        df["time"] = df["time"] + pd.Series(seconds)
        return cls(df)
