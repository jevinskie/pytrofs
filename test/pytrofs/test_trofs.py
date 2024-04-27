#!/usr/bin/env python3

from pytrofs.trofs import dec_tcl_str, enc_tcl_str


def test_dec_tcl_str() -> None:
    assert dec_tcl_str(b"") == ("", 0)
    assert dec_tcl_str(b"a") == ("a", 1)
    assert dec_tcl_str(b"a ") == ("a", 1)
    assert dec_tcl_str(b" a") == ("", 0)
    assert dec_tcl_str(b"{hello world.txt}") == ("hello world.txt", 17)
    assert dec_tcl_str(b"{hello world.txt} ") == ("hello world.txt", 17)
    assert dec_tcl_str(b"{{hello-world.txt}}") == ("{hello-world.txt}", 19)
    assert dec_tcl_str(b"{{hello-world.txt}} ") == ("{hello-world.txt}", 19)
    assert dec_tcl_str(b"{{hello world.txt}}") == ("{hello world.txt}", 19)
    assert dec_tcl_str(b"{{hello world.txt}} ") == ("{hello world.txt}", 19)
    assert dec_tcl_str(b"{hello {} world.txt}") == ("hello {} world.txt", 20)
    assert dec_tcl_str(b"{hello {} world.txt} ") == ("hello {} world.txt", 20)
    assert dec_tcl_str(b'hello-\\"-world.txt') == ('hello-"-world.txt', 18)
    assert dec_tcl_str(b'hello-\\"-world.txt ') == ('hello-"-world.txt', 18)
    assert dec_tcl_str(b"{i-have-a-newline\n-end.txt}") == ("i-have-a-newline\n-end.txt", 27)
    assert dec_tcl_str(b'{i-have-a-newline-\n-and-"-quote.txt}') == (
        'i-have-a-newline-\n-and-"-quote.txt',
        36,
    )
    assert dec_tcl_str(b"{}") == ("", 2)
    assert dec_tcl_str(b'{#{a"b}}') == ('#{a"b}', 8)
    assert dec_tcl_str(b'{{a"b}}') == ('{a"b}', 7)


def test_enc_tcl_str() -> None:
    assert enc_tcl_str("") == b"{}"
