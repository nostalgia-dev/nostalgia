import just
import portray

NDF_PATH = "nostalgia/ndf.py"


def replace_ndf_class():
    ndf_replace = "class NDF:"
    original = just.read(NDF_PATH)
    ndf = [x for x in original.split("\n") if x.startswith("class NDF")][0]
    just.write(original.replace(ndf, ndf_replace), NDF_PATH)
    return original


# remove base pandas from documentation
original_ndf = replace_ndf_class()
try:
    portray.on_github_pages()
except KeyboardInterrupt:
    print("Exiting")
finally:
    # put pandas class back in
    just.write(original_ndf, NDF_PATH)
