import pandas as pd
from nostalgia.times import datetime_from_timestamp
from nostalgia.file_caching import save_df, load_df
from nostalgia.interfaces.post import PostInterface


class RedditPosts(PostInterface):
    vendor = "reddit"

    @classmethod
    def ingest(cls, author):
        from psaw import PushshiftAPI

        api = PushshiftAPI()

        posts = [
            {
                "title": x.title,
                "time": datetime_from_timestamp(x.created_utc, "utc", divide_by_1000=False),
                "url": x.full_link,
                "text": x.selftext,
            }
            for x in api.search_submissions(author=author)
        ]
        posts = pd.DataFrame(posts)
        posts["author"] = author
        save_df(posts, "reddit_posts")

    @classmethod
    def load(cls, nrows=None):
        df = load_df("reddit_posts", nrows)
        return cls(df)
