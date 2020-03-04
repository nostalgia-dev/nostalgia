import os
from datetime import datetime

import just
import pandas as pd

from nostalgia.utils import normalize_name

from nostalgia.times import datetime_from_timestamp
from nostalgia.cache import get_cache
from nostalgia.file_caching import save_df, load_df
from nostalgia.file_caching import get_newline_count, save_newline_count
from nostalgia.file_caching import get_processed_files, save_processed_files
from nostalgia.file_caching import get_last_latest_file, save_last_latest_file
from nostalgia.file_caching import get_last_mod_time, save_last_mod_time


def read_array_of_dict_from_json(fname, key_name=None, nrows=None):
    """
    This is an iterative way to read a json file without having to construct Python elements for everything.
    It can be a lot faster.

    Example data:
    {"participants": {"name": "a", "name": "b", "messages": [{"sender": "a", "time": 123}, {"sender": "b", "time": 124}]}}

    Function call:
    read_array_of_dict_from_json(fname, "messages", nrows=1)

    Returns:
    pd.DataFrame([{"sender": "a", "time": 123}])
    """
    if fname.endswith(".jsonl"):
        if not key_name:
            return pd.read_json(fname, lines=True)
        else:
            return pd.DataFrame([x[key_name] for x in just.read(fname)])

    if nrows is None:
        if not key_name:
            return pd.read_json(fname, lines=fname.endswith(".jsonl"))
        else:
            return pd.DataFrame(just.read(fname)[key_name])

    import ijson

    with open(just.make_path(fname)) as f:
        parser = ijson.parse(f)
        capture = False
        rows = []
        row = {}
        map_key = ""
        num = 0
        for prefix, event, value in parser:
            if num > nrows:
                break
            if prefix == key_name and event == "start_array":
                capture = True
            if not capture:
                continue
            if event == "start_map":
                continue
            elif event == "map_key":
                map_key = value
            elif event == "end_map":
                rows.append(row)
                row = {}
                num += 1
            elif map_key:
                row[map_key] = value
    return pd.DataFrame(rows)


class Loader:
    @classmethod
    def load_data_file_modified_time(
        cls, fname, key_name="", nrows=None, from_cache=True, **kwargs
    ):
        """
        It will load from cache if filename is not changed since last run (and there is a cache).
        If it has changed, it will reprocess and save it in cache (including the modified_time).
        Handles csv, mbox and json currently.
        key_name is only for json.
        nrows is for enabling quickly loading a sample.
        from_cache=False allows ignoring the cache and reprocessing the file.

        Loading the csv, json or mbox file will yield you a DF
        IMPORTANT: assumes you implement `handle_dataframe_per_file`
        This is the post-processing required after the file is loaded, for e.g. converting time
        dropping and adding columns.
        """
        name = fname + "_" + normalize_name(cls.__name__)
        modified_time = os.path.getmtime(os.path.expanduser(fname))
        last_modified = get_last_mod_time(name)
        if modified_time != last_modified or not from_cache:
            if fname.endswith(".csv"):
                data = pd.read_csv(fname, error_bad_lines=False, nrows=nrows, **kwargs)
            elif fname.endswith(".ics"):
                from icalevents.icalevents import events

                evs = events(file=fname, start=datetime.fromtimestamp(0), end=datetime.now())
                data = [
                    {
                        "title": ev.summary,
                        "description": ev.description,
                        "location": ev.location,
                        "start": ev.start,
                        "end": ev.end,
                    }
                    for ev in evs
                ]
                data = pd.DataFrame(data)
            elif fname.endswith(".mbox"):
                import mailbox

                m = mailbox.mbox(fname)
                data = pd.DataFrame(
                    [{l: x[l] for l in ["from", "to", "date", "subject"]} for x in m]
                )
            else:
                data = read_array_of_dict_from_json(fname, key_name, nrows, **kwargs)
            data = cls.handle_dataframe_per_file(data, fname)
            if nrows is None:
                save_df(data, name)
                save_last_mod_time(modified_time, name)
        else:
            data = load_df(name, nrows)
        if nrows is not None:
            data = data.iloc[-nrows:]
        return data

    @classmethod
    def load_json_file_modified_time(cls, fname, nrows=None, from_cache=True, **kwargs):
        name = fname + "_" + normalize_name(cls.__name__)
        modified_time = os.path.getmtime(os.path.expanduser(fname))
        last_modified = get_last_mod_time(name)
        if modified_time != last_modified or not from_cache:
            data = just.read(fname)
            data = cls.handle_json(data, **kwargs)
            data = pd.DataFrame(data)
            if nrows is None:
                save_df(data, name)
                save_last_mod_time(modified_time, name)
        else:
            data = load_df(name)
        if nrows is not None:
            data = data.iloc[-nrows:]
        return data

    @classmethod
    def load_image_texts(cls, glob_pattern_s, nrows=None):
        import pytesseract
        from PIL import Image

        if isinstance(glob_pattern_s, list):
            fnames = set()
            for glob_pattern in glob_pattern_s:
                fnames.update(set(just.glob(glob_pattern)))
            glob_pattern = "_".join(glob_pattern_s)
        else:
            fnames = set(just.glob(glob_pattern))
        name = glob_pattern + "_" + normalize_name(cls.__name__)
        processed_files = get_processed_files(name)
        to_process = fnames.difference(processed_files)
        objects = []

        cache = get_cache("tesseract")

        if nrows is not None:
            if not to_process:
                return load_df(name).iloc[-nrows:]
            else:
                to_process = list(to_process)[-nrows:]
        if to_process:
            for fname in to_process:
                if fname in cache:
                    text = cache[fname]
                else:
                    try:
                        text = pytesseract.image_to_string(Image.open(just.make_path(fname)))
                    except OSError as e:
                        print("ERR", fname, e)
                        continue
                    cache[fname] = text
                time = datetime_from_timestamp(os.path.getmtime(fname), "utc")
                data = {"text": text, "path": fname, "title": fname.split("/")[-1], "time": time}
                objects.append(data)
            data = pd.DataFrame(objects)
            if processed_files and nrows is None:
                data = pd.concat((data, load_df(name)))
            for x in ["time", "start", "end"]:
                if x in data:
                    data = data.sort_values(x)
                    break
            if nrows is None:
                save_df(data, name)
                save_processed_files(fnames | processed_files, name)
        else:
            data = load_df(name)
        if nrows is not None:
            data = data.iloc[-nrows:]
        return data

    @classmethod
    def load_dataframe_per_json_file(cls, glob_pattern, key="", nrows=None):
        fnames = set(just.glob(glob_pattern))
        name = glob_pattern + "_" + normalize_name(cls.__name__)
        processed_files = get_processed_files(name)
        to_process = fnames.difference(processed_files)
        objects = []
        if nrows is not None:
            if not to_process:
                to_process = list(processed_files)[-nrows:]
            else:
                to_process = list(to_process)[-nrows:]
        if to_process:
            print("processing {} files".format(len(to_process)))
            for fname in to_process:
                data = read_array_of_dict_from_json(fname, key, nrows)
                data = cls.handle_dataframe_per_file(data, fname)
                if data is None:
                    continue
                objects.append(data)
            data = pd.concat(objects)
            if processed_files and nrows is None:
                data = pd.concat((data, load_df(name)))
            for x in ["time", "start", "end"]:
                if x in data:
                    data = data.sort_values(x)
                    break
            if nrows is None:
                save_df(data, name)
                save_processed_files(fnames | processed_files, name)
        else:
            data = load_df(name)
        if nrows is not None:
            data = data.iloc[-nrows:]
        return data

    @classmethod
    def load_object_per_newline(cls, fname, nrows=None):
        """
        Iterates over a file containing an object per line (e.g. .jsonl or .txt).
        Will only handle new lines not seen earlier; it detects this by storing the number-of-objects seen.
        You should implement `object_to_row(cls, row)` on your class that returns a dictionary.
        """
        data = []
        name = fname + "_" + normalize_name(cls.__name__)
        newline_count = get_newline_count(name)
        for i, x in enumerate(just.iread(fname)):
            if nrows is None:
                if i < newline_count:
                    continue
            row = cls.object_to_row(x)
            if row is None:
                continue
            data.append(row)
            # breaking at approx 5 rows
            if nrows is not None and i > nrows:
                break
        if data:
            data = pd.DataFrame(data)
            if newline_count and nrows is None:
                data = pd.concat((data, load_df(name)))
            if nrows is None:
                data = save_df(data, name)
                n = i + 1
                save_newline_count(n, name)
        else:
            data = load_df(name)
        if nrows is not None:
            data = data.iloc[-nrows:]
        return data

    @classmethod
    def latest_file_is_historic(cls, glob, key_name="", nrows=None, from_cache=True):
        """
        Glob is for using a wildcard pattern, and the last created file will be loaded.
        See `load_data_file_modified_time` for further reference.
        Returns a pd.DataFrame
        """
        recent = max([x for x in just.glob(glob) if "(" not in x], key=os.path.getctime)
        return cls.load_data_file_modified_time(recent, key_name, nrows, from_cache)
