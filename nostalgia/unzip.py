import tqdm
import sys
import just
import zipfile

if __name__ == "__main__":
    for x in tqdm.tqdm(sys.argv[1:]):
        with zipfile.ZipFile(x, "r") as zip_ref:
            zip_ref.extractall()
        just.remove(x)
