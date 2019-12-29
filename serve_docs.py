import just
import livereload
import portray

NDF_PATH = "nostalgia/ndf.py"


def ignore(x):
    return x.startswith("flycheck")


def replace_ndf_class():
    ndf_replace = "class NDF:"
    original = just.read(NDF_PATH)
    ndf = [x for x in original.split("\n") if x.startswith("class NDF")][0]
    just.write(original.replace(ndf, ndf_replace), NDF_PATH)
    return original


def render_as_html():
    # remove base pandas from documentation
    original_ndf = replace_ndf_class()
    portray.as_html(overwrite=True)
    # put pandas class back in
    just.write(original_ndf, NDF_PATH)


server = livereload.Server()
server.watch("README.md", render_as_html)
server.watch("docs/**", render_as_html)
server.serve(root="site")
