import os
import just
from datetime import datetime
import pandas as pd
from nostalgia.utils import tz, format_latlng
from nostalgia.base_df import DF
import pytesseract
from PIL import Image

# filename = "~/Pictures/youtubetracking.png"
# pytesseract.image_to_string(Image.open(just.make_path(filename)))


class Screenshots(DF):
    @classmethod
    def load(cls, file_dir, nrows=None):
        globs = [os.path.join(file_dir, "*.png"), os.path.join(file_dir, "*.jpg")]
        pic_data = cls.load_image_texts(globs, nrows=nrows)
        pic_data = pd.DataFrame(pic_data)
        return cls(pic_data)
