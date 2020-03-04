import os
import diskcache


def get_cache(name):
    return diskcache.Cache(os.path.expanduser("~/nostalgia_data/cache/" + name))
