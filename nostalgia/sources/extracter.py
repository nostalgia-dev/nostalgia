import os
import just
import zipfile


def load_from_download(ingest_glob, vendor, recent_only=True, delete_existing=True):
    ingest_files = just.glob(ingest_glob)
    if not ingest_files:
        raise ValueError(f"Nothing to extract using {ingest_glob} - Aborting")
    nostalgia_input = "~/nostalgia_data/input/{}".format(vendor)
    if delete_existing:
        just.remove(nostalgia_input, allow_recursive=True)
    elif just.exists(nostalgia_input):
        raise ValueError(f"Cannot overwrite path {nostalgia_input}, pass delete_existing=True")
    fnames = sorted(ingest_files, key=os.path.getctime)
    if recent_only:
        fnames = fnames[-1:]
    for fname in fnames:
        with zipfile.ZipFile(fname, 'r') as zip_ref:
            out = os.path.expanduser(nostalgia_input)
            print("unpacking from", fname, "to", out)
            zip_ref.extractall(out)
