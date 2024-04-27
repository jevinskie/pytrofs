import io
import math
import os
import re
from collections.abc import Iterable
from enum import Enum
from typing import Any, BinaryIO, Final, Self

from attrs import define, field
from path import Path

# https://wiki.tcl-lang.org/page/trofs

TOCDict = dict[Path, "TOCDict"]

trofs_signature: Final = b"\x1atrofs01"
trofs_footer_sz: Final = len(trofs_signature) + 4


def dec_tcl_str(buf: bytes) -> tuple[str, int]:
    dec_buf = bytearray()
    i = 0
    if buf == b"":
        return "", 0
    elif buf[0] == 0x7B:  # b"{"
        brace_level = 1
        i += 1
        while brace_level > 0:
            b = buf[i]
            if b == 0x7B:  # b"{"
                brace_level += 1
            elif b == 0x7D:  # b"}"
                brace_level -= 1
            if brace_level != 0:
                dec_buf.append(b)
            i += 1
        return dec_buf.decode(), i
    else:
        return "", 0


def enc_tcl_str(s: str) -> bytes:
    return b""


class DirEntType(Enum):
    directory = b"D"
    file = b"F"
    link = b"L"


def _is_non_neg(i: Any) -> bool:
    if not isinstance(i, int):
        raise ValueError("Can't call is_non_neg on non-int type.")
    return i >= 0


def _num_digits(i: int) -> int:
    if i == 0:
        return 1
    return math.ceil(math.log10(i + 1))


@define
class DirEnt:
    name: str = field()
    ty: DirEntType = field()
    tgt: str | None = field(default=None)
    sz: int | None = field(default=None, converter=_is_non_neg)
    off: int | None = field(default=None, converter=_is_non_neg)

    def __attrs_post_init__(self) -> None:
        if self.ty is DirEntType.link:
            if self.sz is not None or self.off is not None:
                raise ValueError("Links can't have sz or off set.")
            if self.tgt is None:
                raise ValueError("Links must have a tgt.")
        elif self.ty is DirEntType.file:
            if self.sz is None or self.off is None:
                raise ValueError("Files must have have sz and off set.")
            if self.tgt is None:
                raise ValueError("Files can't have a tgt.")
        elif self.ty is DirEntType.directory:
            if self.sz is None or self.off is None:
                raise ValueError("Directories must have have sz and off set.")
            if self.tgt is None:
                raise ValueError("Directories can't have a tgt.")
        else:
            raise ValueError(f"Unknown DirEntType: {self.ty}")

    @property
    def enc_sz(self) -> int:
        # 5 = <name><SPACE><OPEN CURLY><TYPE><SPACE><params><CLOSE CURLY>
        sz = len(enc_tcl_str(self.name)) + 5
        if self.ty is DirEntType.link:
            assert self.tgt is not None
            sz += len(enc_tcl_str(self.tgt))
        else:
            assert self.sz is not None and self.off is not None
            sz += _num_digits(self.sz) + 1 + _num_digits(self.off)
        return sz

    @property
    def enc_buf(self) -> bytes:
        if self.ty is DirEntType.link:
            assert self.tgt is not None
            return enc_tcl_str(self.name) + b" {L " + enc_tcl_str(self.tgt) + b"}"
        elif self.ty in (DirEntType.file, DirEntType.directory):
            assert isinstance(self.ty.value, bytes)
            return (
                enc_tcl_str(self.name)
                + b" {"
                + self.ty.value
                + b" "
                + str(self.sz).encode()
                + b" "
                + str(self.off).encode()
                + b"}"
            )
        else:
            raise ValueError(f"Unknown DirEntType: {self.ty}")

    @classmethod
    def from_buf(cls, buf: bytes) -> tuple[Self, int]:
        return cls("foo.txt", DirEntType.file, sz=42, off=243), 7


@define
class TOC:
    buf: bytes = field()
    off: int = field()

    @property
    def dirents(self) -> list[DirEnt]:
        dents: list[DirEnt] = []
        blen = len(self.buf)
        clen = 0
        while clen < blen:
            dent, enc_sz = DirEnt.from_buf(self.buf[clen:])
            dents.append(dent)
            clen += enc_sz
        return dents

    @dirents.setter
    def dirents(self, dents: Iterable[DirEnt]) -> None:
        self.buf = b"".join(map(lambda dent: dent.enc_buf, dents))
        pass


class RootTOCException(Exception):
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


def extract_dir(ar_fh: BinaryIO, toc_info: TOC, directory: str | Path) -> None:
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
            child_toc_info = TOC(ar_fh.read(dirent["sz"]), off3)
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


def get_trofs_root_toc_info(ar_fh: BinaryIO) -> TOC:
    orig_pos = ar_fh.tell()
    try:
        ar_fh.seek(-trofs_footer_sz, io.SEEK_END)
        footer = ar_fh.read(trofs_footer_sz)
    except Exception:
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCException(not_enough_footer_bytes=True)
    if not is_trofs_signature(footer):
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCException(bad_signature=footer[: len(trofs_signature)])
    root_toc_sz = int.from_bytes(footer[-4:], "big")
    try:
        ar_fh.seek(-trofs_footer_sz - root_toc_sz, io.SEEK_END)
        root_toc_off = ar_fh.tell()
        root_toc_buf = ar_fh.read(root_toc_sz)
    except Exception:
        ar_fh.seek(orig_pos, io.SEEK_SET)
        raise RootTOCException(not_enough_toc_bytes=root_toc_sz)
    ar_fh.seek(orig_pos, io.SEEK_SET)
    return TOC(root_toc_buf, root_toc_off)


def extract(archive: str | Path, directory: str | Path) -> None:
    archive = Path(archive)
    directory = Path(directory)
    with open(archive, "rb") as ar_fh:
        try:
            root_toc_info = get_trofs_root_toc_info(ar_fh)
        except RootTOCException as e:
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
