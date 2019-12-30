from nostalgia.times import datetime_from_timestamp
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
                "time": datetime_from_timestamp(x.created_utc),
                "url": x.full_link,
                "text": x.selftext,
                "author": author,
            }
            for x in api.search_submissions(author=author)
        ]

        cls.save_df(posts)
