import os
import re
import pandas as pd
from datetime import datetime
import functools
from nostalgia.times import tz

from nostalgia.ndf import NDF

# Add this to your emacs startup init:
# (require 'f)
# (defun log-find-visits ()
#   (when (and buffer-file-name (not (eq last-command "xah-close-current-buffer")))
#       (f-append-text (concat (int-to-string (float-time)) "," buffer-file-name "\n") 'utf-8 "~/nostalgia_data/input/log-emacs-find-visits.txt")))


def git_parent(fname: str) -> str:
    dir_name = os.path.abspath(os.path.join(fname, ".."))
    if dir_name == "/":
        return ""
    elif os.path.exists(os.path.join(dir_name, ".git")):
        return os.path.basename(dir_name)
    return git_parent(dir_name)


class FileVisits(NDF):
    @classmethod
    def load(cls, file_name="~/nostalgia_data/input/log-emacs-find-visits.txt", nrows=None):
        fname = os.path.expanduser(file_name)
        with open(fname) as f:
            results = []
            files = []
            ds = []
            num = 0
            for line in f.read().split("\n"):
                if not line:
                    continue
                y, z = line.split(",", 1)
                if not y:
                    continue
                files.append(z)
                d = datetime.fromtimestamp(float(y), tz)
                ds.append(d)
                if git_parent(z):
                    z = git_parent(z)
                else:
                    for key in ["egoroot/", "/ssh:", "gits/", "site-packages/", "Drive/", "Dropbox/"]:
                        if key in z:
                            z = re.split("[:/]", z.split(key)[1])[0]
                results.append(z)
                if num == nrows:
                    break
                num += 1
        data = pd.DataFrame({"file": files, "name": results, "time": ds})
        return cls(data)
