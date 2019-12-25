import just
import pandas as pd
from psaw import PushshiftAPI
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp
from nostalgia.file_caching import save, load
from nostalgia.interfaces.post import PostInterface


class RedditPosts(PostInterface):
    vendor = "reddit"

    @classmethod
    def ingest(cls, author):
        api = PushshiftAPI()

        posts = list(api.search_submissions(author=author))

        posts = [
            {
                "title": x.title,
                "time": datetime_from_timestamp(x.created_utc, "utc", divide_by_1000=False),
                "url": x.full_link,
                "text": x.selftext,
            }
            for x in posts
        ]
        posts = pd.DataFrame(posts)
        posts["author"] = author
        save(posts, "reddit_posts")

    @classmethod
    def load(cls, nrows=None):
        df = load("reddit_posts")
        if nrows is not None:
            df = df.iloc[-nrows:]
        return cls(df)
