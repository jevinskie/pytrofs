import io
import os
import re
from enum import Enum
from typing import BinaryIO, Final

from attrs import define, field
from path import Path

# https://wiki.tcl-lang.org/page/trofs

TOCDict = dict[Path, "TOCDict"]

trofs_signature: Final[bytes] = b"\x1atrofs01"
trofs_footer_sz: Final[int] = len(trofs_signature) + 4


class DirEntType(Enum):
    directory = b"D"
    file = b"F"
    link = b"L"


@define
class DirEnt:
    ty: DirEntType = field()
    tgt: int = field()
    sz: int | None = field(default=None)
    off: int | None = field(default=None)


@define
class TOCInfo:
    buf: bytes = field()
    off: int = field()


class RootTOCInfoException(Exception):
    def __init__(
        self,
        not_enough_footer_bytes: bool = False,
        bad_signature: bytes | None = None,
        not_enough_toc_bytes: int | None = None,
    ):
        assert (
            not_enough_footer_bytes
            + (bad_signature is not None)
            + (not_enough_toc_bytes is not None)
            == 1
        )
        if not_enough_footer_bytes:
            self.message = f"Not enough footer bytes ({trofs_footer_sz})."
        elif bad_signature is not None:
            self.message = (
                f"Got bad signature '{bad_signature!r}' instead of '{trofs_signature!r}'."
            )
        elif not_enough_toc_bytes is not None:
            self.message = f"Couldn't read {not_enough_footer_bytes} bytes for the root ToC."
        else:
            self.message = "Unknown issue reading root ToC info."


# assume ' ', '{', '}' are not in paths
_toc_re = re.compile(
    rb"(?P<name>[^ {}]+) {((?P<ty>F|D) (?P<sz>\d+) (?P<off>\d+)|L (?P<tgt>[^ {}]+))}(?: )?"
)


def extract_dir(ar_fh: BinaryIO, toc_info: TOCInfo, directory: str | Path) -> None:
    directory = Path(directory)
    dirents = {}
    for m in _toc_re.finditer(toc_info.buf):
        toc = m.groupdict()
        assert toc["name"] is not None
        name_bytes = toc["name"]
        assert isinstance(name_bytes, bytes)
        name = name_bytes.decode()
        ty = toc["ty"]
        sz = int(toc["sz"]) if toc["sz"] is not None else None
        off1 = toc_info.off - int(toc["off"]) if toc_info.off is not None else None
        tgt = toc["tgt"]
        dirents[name] = {"ty": ty, "sz": sz, "off": off1, "tgt": tgt}

    for name, dirent in dirents.items():
        assert isinstance(name, str)
        path = directory / name
        if dirent["ty"] == b"F":
            off2 = int(dirent["off"]) if dirent["off"] is not None else None
            assert off2 is not None
            ar_fh.seek(off2, io.SEEK_SET)
            assert dirent["sz"] is not None and isinstance(dirent["sz"], int)
            buf = ar_fh.read(dirent["sz"])
            os.makedirs(path.dirname(), exist_ok=True)
            with open(path, "wb") as f:
                f.write(buf)
        elif dirent["ty"] == b"D":
            off3 = int(dirent["off"]) if dirent["off"] is not None else None
            assert off3 is not None
            ar_fh.seek(off3, io.SEEK_SET)
            assert dirent["sz"] is not None and isinstance(dirent["sz"], int)
            child_toc_info = TOCInfo(ar_fh.read(dirent["sz"]), off3)
            # print(f"child '{name}' off: {off} toc: {child_toc_buf}")
            os.makedirs(path, exist_ok=True)
            extract_dir(ar_fh, child_toc_info, path)
        elif dirent["tgt"]:
            assert isinstance(dirent["tgt"], str)
            os.makedirs(path.dirname(), exist_ok=True)
            os.link(path, dirent["tgt"])
        else:
            raise ValueError(f"unknown ToC type for {name}")


def is_trofs_signature(footer: bytes) -> bool:
    return footer[: len(trofs_signature)] == trofs_signature


def get_trofs_root_toc_info(ar_fh: BinaryIO) -> TOCInfo:
    orig_pos = ar_fh.tell()
    try:
        ar_fh.seek(-trofs_footer_sz, io.SEEK_END)
        footer = ar_fh.read(trofs_footer_sz)
    except Exception:
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCInfoException(not_enough_footer_bytes=True)
    if not is_trofs_signature(footer):
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCInfoException(bad_signature=footer[: len(trofs_signature)])
    root_toc_sz = int.from_bytes(footer[-4:], "big")
    try:
        ar_fh.seek(-trofs_footer_sz - root_toc_sz, io.SEEK_END)
        root_toc_off = ar_fh.tell()
        root_toc_buf = ar_fh.read(root_toc_sz)
    except Exception:
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCInfoException(not_enough_toc_bytes=root_toc_sz)
    ar_fh.seek(orig_pos, io.SEEK_SET)
    return TOCInfo(root_toc_buf, root_toc_off)


def extract(archive: str | Path, directory: str | Path) -> None:
    archive = Path(archive)
    directory = Path(directory)
    with open(archive, "rb") as ar_fh:
        try:
            root_toc_info = get_trofs_root_toc_info(ar_fh)
        except RootTOCInfoException as e:
            raise ValueError(f"File '{archive}' is not a valid trofs archive. Exception:\n{e}")
        os.makedirs(directory, exist_ok=True)
        extract_dir(ar_fh, root_toc_info, directory)


def create(archive: str | Path, directory: str | Path) -> None:
    archive = Path(archive)
    directory = Path(directory).normpath()
    with open(archive, "wb") as ar_fh:
        ar_fh.write(b"\x1a")

        tocs: dict[Path, list[bytes]] = {}
        # ordered dictionary hack since path doesn't return root dir first
        tocs[Path("")] = []
        dir_parents = {}
        file_sz = {}
        file_off = {}
        for file in Path(directory).walk():
            trunc_path = Path(file.removeprefix(directory))
            parent = Path(file.parent.removeprefix(directory))
            toc: bytes = file.name.encode() + b" "
            if file.isfile():
                sz = file.size
                off = ar_fh.tell()
                file_sz[trunc_path] = sz
                file_off[trunc_path] = off
                rbuf = file.read_bytes()
                assert len(rbuf) == sz
                ar_fh.write(rbuf)
                toc += b"{F}"
            elif file.islink():
                tgt = file.readlink().encode()
                toc += b"{L " + tgt + b"}"
            elif file.isdir():
                toc += b"{D}"
                if trunc_path not in tocs:
                    tocs[trunc_path] = []
                else:
                    raise KeyError("supposed to happen?")
                dir_parents[trunc_path] = parent
            else:
                raise ValueError(f"File type for '{file}' not supported. stat: {file.stat}")
            if parent in tocs:
                tocs[parent].append(toc)
            else:
                tocs[parent] = [toc]

        tocs_walked = tocs
        tocs_sz: dict[Path, int] = {}
        tocs_off: dict[Path, int] = {}
        for path, toc_list in reversed(tocs_walked.items()):
            toc_off = ar_fh.tell()
            tocs_updated: list[bytes] = []
            for e in toc_list:
                p = path + "/" + e[:-4].decode()
                if e.endswith(b" {F}"):
                    e = e.removesuffix(b"}")
                    off = toc_off - file_off[p]
                    e += f" {file_sz[p]} {off}}}".encode()
                elif e.endswith(b" {D}"):
                    e = e.removesuffix(b"}")
                    off = toc_off - tocs_off[p]
                    e += f" {tocs_sz[p]} {off}}}".encode()
                else:
                    pass
                tocs_updated.append(e)
            toc_buf = b" ".join(tocs_updated)
            tocs_sz[path] = len(toc_buf)
            tocs_off[path] = toc_off
            ar_fh.write(toc_buf)

        root_toc_sz = tocs_sz[Path("")]
        ar_fh.write(trofs_signature)
        ar_fh.write(root_toc_sz.to_bytes(4, "big"))
