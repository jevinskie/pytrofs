import io
import os
import re

from path import Path

# https://wiki.tcl-lang.org/page/trofs

# assume ' ', '{', '}' are not in paths
_toc_re = re.compile(
    b"(?P<name>[^ {}]+) {((?P<ty>F|D) (?P<sz>\d+) (?P<off>\d+)|L (?P<tgt>[^ {}]+))}(?: )?"
)


def extract_dir(ar, toc_buf, toc_off, directory):
    dirents = {}
    for m in _toc_re.finditer(toc_buf):
        toc = m.groupdict()
        name = toc["name"]
        ty = toc["ty"]
        sz = int(toc["sz"]) if toc["sz"] else None
        off = toc_off - int(toc["off"]) if toc["off"] else None
        tgt = toc["tgt"]
        dirents[name] = {"ty": ty, "sz": sz, "off": off, "tgt": tgt}

    for name, dirent in dirents.items():
        path = directory + b"/" + name
        off = dirent["off"]
        if dirent["ty"] == b"F":
            ar.seek(off, io.SEEK_SET)
            buf = ar.read(dirent["sz"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(buf)
        elif dirent["ty"] == b"D":
            ar.seek(off, io.SEEK_SET)
            child_toc_buf = ar.read(dirent["sz"])
            # print(f"child '{name}' off: {off} toc: {child_toc_buf}")
            os.makedirs(path, exist_ok=True)
            extract_dir(ar, child_toc_buf, off, path)
        elif dirent["tgt"]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.link(path, dirent["tgt"])
        else:
            raise ValueError(f"unknown ToC type for {name}")


def extract(archive, directory):
    with open(archive, "rb") as ar:
        ar.seek(-12, io.SEEK_END)
        trailer = ar.read(12)
        assert trailer.startswith(b"\x1atrofs01")
        root_toc_sz = int.from_bytes(trailer[-4:], "big")
        # print(f"root_toc_sz: {root_toc_sz}")
        ar.seek(-12 - root_toc_sz, io.SEEK_END)
        root_toc_off = ar.tell()
        # print(f"root toc off: {root_toc_off}")
        root_toc_buf = ar.read(root_toc_sz)
        # print(f"root_toc: {root_toc_buf.decode('utf-8')}")
        os.makedirs(directory, exist_ok=True)
        extract_dir(ar, root_toc_buf, root_toc_off, directory.encode("utf-8"))


def create(archive, directory):
    directory = Path(directory).normpath()
    with open(archive, "wb") as ar:
        ar.write(b"\x1a")

        tocs = {}
        # ordered dictionary hack since path doesn't return root dir first
        tocs[""] = []
        dir_parents = {}
        file_sz = {}
        file_off = {}
        for file in Path(directory).walk():
            trunc_path = file.removeprefix(directory)
            parent = file.parent.removeprefix(directory)
            toc = file.name.encode("utf-8") + b" "
            if file.isfile():
                sz = file.size
                off = ar.tell()
                file_sz[trunc_path] = sz
                file_off[trunc_path] = off
                rbuf = file.read_bytes()
                assert len(rbuf) == sz
                ar.write(rbuf)
                toc += b"{F}"
            elif file.islink():
                tgt = file.readlink().encode("utf-8")
                toc += b"{L " + tgt + b"}"
            elif file.isdir():
                toc += b"{D}"
                if trunc_path not in tocs:
                    tocs[trunc_path] = []
                else:
                    raise KeyError("supposed to happen?")
                dir_parents[trunc_path] = parent
            else:
                raise ValueError(f"File type not supported {file}")
            if parent in tocs:
                tocs[parent].append(toc)
            else:
                tocs[parent] = [toc]

        tocs_walked = tocs
        tocs_sz = {}
        tocs_off = {}
        for path, toc in reversed(tocs_walked.items()):
            toc_off = ar.tell()
            tocs_updated = []
            for e in toc:
                p = path + "/" + e[:-4].decode("utf-8")
                if e.endswith(b" {F}"):
                    e = e.removesuffix(b"}")
                    off = toc_off - file_off[p]
                    e += f" {file_sz[p]} {off}}}".encode("utf-8")
                elif e.endswith(b" {D}"):
                    e = e.removesuffix(b"}")
                    off = toc_off - tocs_off[p]
                    e += f" {tocs_sz[p]} {off}}}".encode("utf-8")
                else:
                    pass
                tocs_updated.append(e)
            toc_buf = b" ".join(tocs_updated)
            tocs_sz[path] = len(toc_buf)
            tocs_off[path] = toc_off
            ar.write(toc_buf)

        root_toc_sz = tocs_sz[""]
        ar.write(b"\x1atrofs01")
        ar.write(root_toc_sz.to_bytes(4, "big"))
