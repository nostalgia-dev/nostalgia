import just
import pandas as pd
from psaw import PushshiftAPI
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp
from nostalgia.source_to_fast import save, load
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
        save(posts, "reddit_posts_" + author)

    @classmethod
    def load(cls, author, nrows=None):
        return cls(load("reddit_posts_" + author))
