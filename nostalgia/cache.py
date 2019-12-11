import os
import diskcache


def get_cache(name):
    return diskcache.Cache(os.path.expanduser("~/.nostalgia/cache/" + name))
