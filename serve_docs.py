import just
import livereload
import portray

NDF_PATH = "nostalgia/ndf.py"


def ignore(x):
    return "lycheck" in x


def replace_ndf_class():
    ndf_replace = "class NDF:"
    original = just.read(NDF_PATH)
    ndf = [x for x in original.split("\n") if x.startswith("class NDF")][0]
    just.write(original.replace(ndf, ndf_replace), NDF_PATH)
    return original


def render_as_html():
    # remove base pandas from documentation
    original_ndf = replace_ndf_class()
    try:
        portray.as_html(overwrite=True)
    except KeyboardInterrupt:
        print("Exiting")
    # put pandas class back in
    finally:
        just.write(original_ndf, NDF_PATH)


server = livereload.Server()
server.watch("README.md", render_as_html, ignore=ignore)
server.watch("docs/**", render_as_html, ignore=ignore)
server.watch("docs/**/*.md", render_as_html, ignore=ignore)
server.serve(root="site")
