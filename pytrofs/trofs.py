import io

# https://wiki.tcl-lang.org/page/trofs


def extract(archive, directory):
    print(f"extract ar: {archive} dir: {directory}")
    with open(archive, "rb") as ar:
        ar.seek(-12, io.SEEK_END)
        trailer = ar.read(12)
        assert trailer.startswith(b"\x1atrofs01")
        root_toc_sz = int.from_bytes(trailer[-4:], "big")
        print(f"root_toc_sz: {root_toc_sz}")
        ar.seek(-12 - root_toc_sz, io.SEEK_END)
        root_toc_buf = ar.read(root_toc_sz)
        print(f"root_toc: {root_toc_buf.decode('utf-8')}")


def create(archive, directory):
    print(f"create ar: {archive} dir: {directory}")
