import os
from nostalgia.file_caching import save_df, load_df
from nostalgia.ndf import NDF


class Screenshots(NDF):
    @classmethod
    def ingest(cls, file_dir, nrows=None):
        """ Process a picture folder. Takes ~1s per image to OCR. """
        globs = [os.path.join(file_dir, "*.png"), os.path.join(file_dir, "*.jpg")]
        pic_data = cls.load_image_texts(globs, nrows=nrows)
        save_df(pic_data, "screenshots")

    @classmethod
    def load(cls, nrows=None):
        df = load_df("screenshots", nrows)
        return cls(df)
