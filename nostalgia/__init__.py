import just

ENTRY = "~/.nostalgia/nostalgia_entry.py"
if not just.exists("~/.nostalgia/nostalgia_entry.py"):
    just.write("", ENTRY)
