import os
import shutil

import just
from nostalgia.ndf import NDF


class Twitter(NDF):
    vendor = "twitter"
    ingest_settings = {
        "ingest_glob": "~/Downloads/twitter-20*-*.zip",
        "recent_only": False,
        "delete_existing": False
    }

    @classmethod
    def ingest(cls):
        super().ingest()

        # replace first line
        from_file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/tweet.js")
        to_file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/tweet.json")
        
        # Kudos https://stackoverflow.com/a/14947384
        from_file = open(from_file_path, "r")
        line = from_file.readline()

        # Kudos https://stackoverflow.com/a/33141629
        line = line[line.find('['):]

        to_file = open(to_file_path, "w")
        to_file.write(line)

        shutil.copyfileobj(from_file, to_file)
        from_file.close()
        to_file.close()

    """
    @classmethod
    def load(cls, nrows=None):
        files = just.glob("~/nostalgia_data/input/twitter/*.json")
    """