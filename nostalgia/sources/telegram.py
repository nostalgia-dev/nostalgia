from collections import defaultdict

import just
import pandas as pd

from nostalgia.interfaces.chat import ChatInterface
from nostalgia.times import datetime_from_format


class Telegram(ChatInterface):
    vendor = "telegram"
    ingest_settings = {
        "ingest_glob": "~/Downloads/Telegram Desktop/*/chats/chat_*/message*.html",
        "recent_only": False,
        "delete_existing": False,
    }

    sender_column = "sender"

    @property
    def me(self):
        return self["sender"].value_counts().idxmax()

    @classmethod
    def ingest(cls, *args, **kwargs):
        results = defaultdict(list)
        glob = just.glob(cls.ingest_settings["ingest_glob"])
        for i, fname in enumerate(glob):
            print(i, len(glob), fname)
            tree = just.read_tree(fname)
            last_from_name = None
            conversation_title = None
            for node in tree.iter():
                if conversation_title is None and node.tag == "a":
                    conversation_title = node.xpath("./div/text()")[0].strip()
                class_name = node.attrib.get("class") or ""
                if class_name == "body":
                    from_name = node.xpath("./div[@class = 'from_name']/text()")
                    from_name = from_name[0] if from_name else last_from_name
                    from_name = from_name.strip()
                    last_from_name = from_name
                    date = node.xpath("./div[@class = 'pull_right date details']/@title")
                    if not date:
                        continue
                    if "+" in date[0]:
                        date = datetime_from_format(date[0], "%d.%m.%Y %H:%M:%S %Z%z", None)
                    else:
                        date = datetime_from_format(date[0], "%d.%m.%Y %H:%M:%S", None)
                    text = node.xpath("./div[@class = 'text']/text()")
                    if not text:
                        continue
                    text = text[0].strip()
                    results[conversation_title].append([date, from_name, text])

        df = pd.DataFrame(
            sum([[(conv_title, *row) for row in rows] for conv_title, rows in results.items()], []),
            columns=["conversation", "dt", "sender", "text"],
        )
        cls.save_df(df.drop_duplicates())
