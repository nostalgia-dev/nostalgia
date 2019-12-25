import os
import just
from datetime import datetime
import pandas as pd
from nostalgia.times import tz
from nostalgia.utils import format_latlng
from nostalgia.file_caching import save, load
from nostalgia.ndf import NDF
import pytesseract
from PIL import Image

# filename = "~/Pictures/youtubetracking.png"
# pytesseract.image_to_string(Image.open(just.make_path(filename)))


class Screenshots(NDF):
    @classmethod
    def ingest(cls, file_dir, nrows=None):
        globs = [os.path.join(file_dir, "*.png"), os.path.join(file_dir, "*.jpg")]
        pic_data = cls.load_image_texts(globs, nrows=nrows)
        pic_data = pd.DataFrame(pic_data)
        save(pic_data, "screenshots")

    @classmethod
    def load(cls, nrows=None):
        df = load("screenshots")
        if nrows is not None:
            df = df.iloc[-nrows:]
        return cls(df)
