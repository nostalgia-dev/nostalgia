import re
import just
import pandas
from nostalgia.times import datetime_from_timestamp
from nostalgia.sources.facebook import Facebook
from nostalgia.interfaces.post import PostInterface


class FacebookPosts(Facebook, PostInterface):
    @classmethod
    def handle_json(cls, data):
        posts = []
        for post in data:
            if "data" not in post or not isinstance(post["data"], list):
                continue
            location = "self"
            title = post.get("title", "")
            location_res = re.findall(
                "(?:on|to) ([^']+)'s? [tT]imeline|posted in ([^.]+)|was with ([^.]+)[.]$", title
            )
            if location_res:
                location = [x for x in location_res[0] if x][0]
            for x in post["data"]:
                if "post" not in x:
                    continue
                row = {
                    "location": location,
                    "title": x["post"],
                    "time": datetime_from_timestamp(post['timestamp']),
                }
                posts.append(row)
        return posts

    @classmethod
    def load(cls, nrows=None):
        data = cls.load_json_file_modified_time(
            "~/nostalgia_data/input/facebook/posts/your_posts_1.json"
        )
        return cls(data)
