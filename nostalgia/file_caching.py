import re
import just
import os
import pandas as pd


def slugify(name):
    return re.sub(r'[\W_]+', '-', name)


def file_modified_since_last(fname, name):
    path = just.make_path("~/nostalgia_data/seen/" + slugify(name) + ".json")
    last_run_mt = float(just.read(path, no_exist=0))
    modified_time = os.path.getmtime(fname)
    if last_run_mt != modified_time:
        return modified_time
    else:
        return None


def get_last_mod_time(name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.read(path, no_exist=0.0)


def save_last_mod_time(last_mod_time, name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.write(last_mod_time, path)


def get_last_latest_file(name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.read(path, no_exist=0)


def save_last_latest_file(latest_file, name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.write(latest_file, path)


def get_newline_count(name):
    """ counts by row numbers in a file """
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.read(path, no_exist=0)


def save_newline_count(n, name):
    """ counts by row numbers in a file """
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return just.write(n, path)


def get_processed_files(name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    return set(just.read(path, no_exist=[]))


def save_processed_files(fnames, name):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    just.write(fnames, path)


def check_seen(name, value):
    path = "~/nostalgia_data/seen/" + slugify(name) + ".json"
    is_new = True
    res = just.read(path, no_exist=False)
    if res:
        if isinstance(value, tuple):
            value = list(value)
        is_new = res != value
    if is_new:
        just.write(value, path)
    return is_new


def make_path(name):
    dir_name = os.path.expanduser("~/nostalgia_data/dfs/")
    just.mkdir(dir_name, 0x700)
    return dir_name + slugify(name)


def save_df(df, name):
    path = make_path(name) + ".parquet"
    df = pd.DataFrame(df)
    for x in ["time", "start", "end"]:
        if x in df:
            df = df.sort_values(x)
            break
    df = df.reset_index(drop=True)
    if "index" in df.columns:
        df.drop("index", axis=1, inplace=True)
    if "level_0" in df.columns:
        df.drop("level_0", axis=1, inplace=True)
    try:
        df.to_parquet(path, compression="zstd", allow_truncated_timestamps=True)
    except Exception as e:
        print("ERROR with", name)
        for x in df.columns:
            print(x, sum([str(y)[:1] == "{" for y in df[x]]))
        raise e
    return df


def load_df(name, nrows=None):
    path = make_path(name) + ".parquet"
    data = pd.read_parquet(path)
    if nrows is not None:
        data = data.iloc[-nrows:]
    return data
