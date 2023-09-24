from pathlib import Path
import sys
import pandas as pd
import just
from cliche import cli, main
import inspect

try:
    import google.api_core
    import google.auth
    import google.oauth2
except:
    pass

ENTRY = Path("~/nostalgia_data/nostalgia_entry.py").expanduser()
if not ENTRY.exists():
    just.write("", str(ENTRY))

from nostalgia.ndf import NDF
from nostalgia.times import parse_datetime
import pkgutil
import nostalgia.sources
import nostalgia.interfaces


@cli
def modules(only_registered: bool = False):
    """Show all or connected sources"""
    mods = register_modules() if only_registered else MODULES
    return sorted([x.class_df_name() for x in mods])


MODULES = {}
INGESTERS = {}


def process_modules(paths: list[str], depth=0):
    todos = []
    for importer, modname, ispkg in pkgutil.iter_modules(paths):
        m = importer.find_module(modname).load_module(modname)
        if ispkg:
            process_modules([f"{x}/{modname}" for x in paths], depth + 1)
        for var_name in dir(m):
            var = getattr(m, var_name)
            if not hasattr(var, "mro"):
                continue
            # print(importer, modname, ispkg)
            if var.__module__.startswith("nostalgia.interfaces"):
                continue
            var_module = f"{var.__module__}"
            has_ingester_parent = set(var.mro()).intersection(set(INGESTERS.values()))
            if not has_ingester_parent and hasattr(var, "ingest_settings") and depth == 0:
                INGESTERS[var_module] = var
            if "nostalgia.sources" in var.__module__:
                continue
            if var_name != "NDF" and "NDF" in str(var.mro()):
                if not ispkg:
                    module_fname = inspect.getfile(var)
                    if module_fname not in MODULES:
                        MODULES[module_fname] = var
                else:
                    process_modules([f"{x}/{modname}" for x in paths], depth + 1)


process_modules(nostalgia.sources.__path__)

MODULES = set(MODULES.values())

INGESTERS = {k: v for k, v in INGESTERS.items() if "nostalgia.sources" not in k}

INTERFACES = set()
for importer, modname, ispkg in pkgutil.iter_modules(nostalgia.interfaces.__path__):
    m = importer.find_module(modname).load_module(modname)
    for var_name in dir(m):
        var = getattr(m, var_name)
        if not hasattr(var, "mro"):
            continue
        if var_name != "NDF" and "NDF" in str(var.mro()):
            INTERFACES.add(var)


def register_modules():
    modules = {}
    for x in MODULES:
        try:
            modules[x] = x.register()
        except (ValueError, ImportError, FileNotFoundError, IndexError):
            pass
    return modules


@cli
def overview(load: bool = False):
    """Show table of sources and optionally show count of rows when loading"""
    registered_modules = register_modules()
    return (
        pd.DataFrame(
            [
                {
                    "name": x.class_df_name(),
                    "vendor": x.vendor or "",
                    "registered": "T" * (x in registered_modules),
                    "ingestable": "T" * hasattr(x, "ingest_settings"),
                    "num_rows": "?" if not load or x not in registered_modules else x.load().shape[0],
                }
                for x in MODULES
            ]
        )
        .set_index("name")
        .sort_values(["vendor", "name"])
    )


m = None


def refresh_data(every_secs: int):
    import time

    global m
    time.sleep(3)
    registered_modules = register_modules()
    while True:
        m = {x.class_df_name(): x.load() for x in registered_modules}
        time.sleep(every_secs)
        print(m.keys())


@cli
def interactive(color="Neutral", refresh_data_every_secs: int = 120):
    global m

    import matplotlib.pyplot as plt
    from IPython.terminal.embed import InteractiveShellEmbed

    shell = InteractiveShellEmbed()
    shell.enable_matplotlib()
    from threading import Thread

    refresh_thread = Thread(target=refresh_data, args=(refresh_data_every_secs,))
    refresh_thread.start()

    exec(open("/home/pascal/egoroot/emp/.emacs.d/init/python_importer.py").read())
    shell(header="Welcome to Interactive Nostalgia, advised to run: `%pylab`", colors=color)


@cli
def ingest(name: str | None = None, password: str | None = None):
    """Ingest source, e.g. twitter or google"""
    if name is not None:
        ingester = INGESTERS[name]
        if password is not None:
            ingester.ingest(password=password)
        else:
            ingester.ingest()
    else:
        return [x for x in INGESTERS]


@cli
def config():
    """Allow changing config values"""
    return "NOT YET"


@cli
def timeline(port: int = 5552):
    """Run the timeline in dev mode"""
    import os
    import sys

    path = os.path.abspath(os.path.join(__file__, "../../../timeline"))
    sys.path.append(path)
    os.chdir(path)
    import timeline

    timeline.app.run(host="0.0.0.0", port=port)
