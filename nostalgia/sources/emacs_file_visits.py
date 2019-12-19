import os
import re
import pandas as pd
from datetime import datetime
from nostalgia.utils import tz

from nostalgia.ndf import NDF

# (require 'f)
# (defun log-find-visits ()
#   (when (and buffer-file-name (not (eq last-command "xah-close-current-buffer")))
#       (f-append-text (concat (int-to-string (float-time)) "," buffer-file-name "\n") 'utf-8 "~/.nostalgia/input/log-emacs-find-visits.txt")))


class FileVisits(NDF):
    @classmethod
    def load(cls, file_name="~/.nostalgia/input/log-emacs-find-visits.txt", nrows=None):
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
                for key in ["egoroot/", "/ssh:", "gits/", "site-packages/"]:
                    if key in z:
                        z = re.split("[:/]", z.split(key)[1])[0]
                results.append(z)
                if num == nrows:
                    break
                num += 1
        data = pd.DataFrame({"file": files, "name": results, "time": ds})
        return cls(data)
