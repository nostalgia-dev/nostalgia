import just

ENTRY = "~/nostalgia_data/nostalgia_entry.py"
if not just.exists("~/nostalgia_data/nostalgia_entry.py"):
    just.write("", ENTRY)

from nostalgia.ndf import NDF
