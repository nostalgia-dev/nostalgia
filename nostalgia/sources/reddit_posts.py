from psaw import PushshiftAPI
from nostalgia.ndf import NDF
from nostalgia.utils import datetime_from_timestamp
from nostalgia.source_to_fast import save, load
import just


class Posts(NDF):
    vendor = "reddit"

    @classmethod
    def download(cls, author):
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
