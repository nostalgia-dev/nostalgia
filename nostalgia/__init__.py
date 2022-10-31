from pathlib import Path
import sys
import just
from cliche import cli, main

ENTRY = Path("~/nostalgia_data/nostalgia_entry.py").expanduser()
if not ENTRY.exists():
    just.write("", str(ENTRY))

from nostalgia.ndf import NDF
from nostalgia.times import parse_datetime


@cli
def modules():
    sys.path.append(str(ENTRY.parent))
    import importlib

    return [x for x in dir(importlib.import_module("nostalgia_entry")) if x[0] != "_" and x[0] == x[0].upper()]


@cli
def config():
    return "NOT YET"
