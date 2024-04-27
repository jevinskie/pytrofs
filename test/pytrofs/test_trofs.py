#!/usr/bin/env python3

from pytrofs.trofs import dec_tcl_str


def test_dec_tcl_str() -> None:
    assert dec_tcl_str(b"") == ("", 0)
    assert dec_tcl_str(b"a") == ("a", 1)
    assert dec_tcl_str(b"a ") == ("a", 1)
    assert dec_tcl_str(b" a") == ("", 0)
    assert dec_tcl_str(b"{hello world.txt}") == ("hello world.txt", 17)
    assert dec_tcl_str(b"{hello world.txt} ") == ("hello world.txt", 17)
    assert dec_tcl_str(b"{{hello world.txt}}") == ("{hello world.txt}", 19)
    assert dec_tcl_str(b"{{hello world.txt}} ") == ("{hello world.txt}", 19)
    assert dec_tcl_str(b"{hello {} world.txt}") == ("hello {} world.txt", 20)
    assert dec_tcl_str(b"{hello {} world.txt} ") == ("hello {} world.txt", 20)
