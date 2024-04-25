#!/usr/bin/env python3

from lark import Lark
from rich import print

# lexer='dynamic'
lexer = "dynamic_complete"

toc_parser = Lark(open("./pytrofs/toc.lark"), start="toc", strict=True, lexer=lexer)
fname_parser = Lark(open("./pytrofs/toc.lark"), start="filename", strict=True, lexer=lexer)
parameters_parser = Lark(open("./pytrofs/toc.lark"), start="parameters", strict=True, lexer=lexer)


plain_toc_entry_str = "world.txt {F 14 42}"
print(toc_parser.parse(plain_toc_entry_str))

bracketed_fname = "{hello world.txt}"
print(fname_parser.parse(bracketed_fname))

bracketed_toc_entry_str = "{hello world.txt} {F 14 42}"
print(toc_parser.parse(bracketed_toc_entry_str))

braces_fname = "nested-far-{-{-}-}-brackets.txt"
print(fname_parser.parse(braces_fname))

quoted_symlink_fname = 'i-have-a-middle-\\"-quote-symlink.txt'
print(fname_parser.parse(quoted_symlink_fname))

quoted_fname = 'i-have-a-middle-\\"-quote.txt'
print(fname_parser.parse(quoted_fname))

dumb_entry_detail = '{L i-have-a-middle-\\"-quote.txt}'
print(parameters_parser.parse(dumb_entry_detail))

quoted_toc_entry_str = (
    'i-have-a-middle-\\"-quote-symlink.txt {L ../files-with-quotes/i-have-a-middle-\\"-quote.txt}'
)
print(quoted_toc_entry_str)
# quoted_toc_entry_str = 'i-have-a-middle-\\\"-quote-symlink.txt {L i-have-a-middle-fart-quote.txt}'
# quoted_toc_entry_str = 'i-have-a-middle-quote-symlink.txt {L i-have-a-middle-fart-quote.txt}'
# quoted_toc_entry_str = 'a.txt {L b.txt}'
# quoted_toc_entry_bytes = quoted_toc_entry_str.encode()
# print(quoted_toc_entry_str)
# print(quoted_toc_entry_bytes)
# print(quoted_toc_entry_bytes.hex(" "))
# print(quoted_toc_entry_str)
print(toc_parser.parse(quoted_toc_entry_str))

bracketed_toc_entry_str2 = (
    "i-end-with-a-space-symlink.txt-space {L {../files-with-spaces/i-end-with-a-space.txt }}"
)
print(toc_parser.parse(bracketed_toc_entry_str2))

braces_toc_entry = "nested-far-{-{-}-}-brackets.txt {L ../files-with-brackets/i-have-two-open-{-{-}-}-bracket-pair-farther-nested.txt}"
print(toc_parser.parse(braces_toc_entry))

a = ' space-i-start-with-a-space-and-have-a-\\"-in-the-middle-symlink.txt-space {L {../files-with-spaces/ i-start-and-end-with-a-space-and-have-a-"-in-the-middle.txt }}'
print(toc_parser.parse(a))

b = '{space-i-start-with-a-space-and-have-a-"-in-the-middle-symlink.txt } {L {../files-with-spaces/ i-start-and-end-with-a-space-and-have-a-"-in-the-middle.txt }}'
print(toc_parser.parse(b))

c = "i-have-unbalanced-\\{\\}-\\}-bracket-far1-opposite.txt {F 49 260}"
print(toc_parser.parse(c))

df = "{{-i-am-surrounded-with-brackets.txt-}}"
print(fname_parser.parse(df))

d = "{{-i-am-surrounded-with-brackets.txt-}} {F 30 821}"
print(d)
print(toc_parser.parse(d))

e = "i-have-unbalanced-\\{\\}-\\}-bracket-far1-opposite.txt {F 49 260} {{-i-am-surrounded-with-brackets.txt-}} {F 30 821}"
print(e)
print(toc_parser.parse(e))

big_bytes = bytes.fromhex(
    "69 2D 68 61 76 65 2D 74 77 6F 2D 5C 7B 2D 6E 6F 6E 2D 61 64 6A 61 63 65 6E 74 2D 5C 7B 2D 62 72 61 63 6B 65 74 73 2D 66 61 72 2E 74 78 74 20 7B 46 20 33 32 20 38 31 7D 20 69 2D 65 6E 64 2D 77 69 74 68 2D 61 6E 2D 6F 70 65 6E 2D 62 72 61 63 6B 65 74 2E 74 78 74 2D 5C 7B 20 7B 46 20 32 37 20 33 36 39 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 5C 7D 5C 7D 2D 62 72 61 63 6B 65 74 2D 6E 65 61 72 2D 6F 70 70 6F 73 69 74 65 2E 74 78 74 20 7B 46 20 34 39 20 38 37 30 7D 20 5C 7B 2D 69 2D 62 65 67 69 6E 2D 77 69 74 68 2D 61 2D 62 72 61 63 6B 65 74 2E 74 78 74 20 7B 46 20 32 33 20 31 33 31 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 5C 7B 5C 7B 2D 62 72 61 63 6B 65 74 73 2D 6E 65 61 72 2E 74 78 74 20 7B 46 20 33 33 20 35 36 34 7D 20 5C 7D 2D 69 2D 62 65 67 69 6E 2D 77 69 74 68 2D 61 2D 63 6C 6F 73 65 64 2D 62 72 61 63 6B 65 74 2E 74 78 74 20 7B 46 20 32 39 20 36 34 37 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 5C 7D 2D 6E 6F 6E 2D 61 64 6A 61 63 65 6E 74 2D 5C 7D 2D 62 72 61 63 6B 65 74 73 2D 66 61 72 2E 74 78 74 20 7B 46 20 33 32 20 37 37 30 7D 20 69 2D 65 6E 64 2D 77 69 74 68 2D 61 2D 62 72 61 63 6B 65 74 2E 74 78 74 2D 5C 7D 20 7B 46 20 32 31 20 37 39 31 7D 20 69 2D 68 61 76 65 2D 6F 70 65 6E 2D 7B 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2D 61 64 6A 61 63 65 6E 74 2E 74 78 74 20 7B 46 20 34 38 20 36 39 35 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 6F 70 65 6E 2D 7B 2D 7B 2D 7D 2D 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2D 66 61 72 74 68 65 72 2D 6E 65 73 74 65 64 2E 74 78 74 20 7B 46 20 35 34 20 36 31 38 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 5C 7D 5C 7D 2D 62 72 61 63 6B 65 74 73 2D 6E 65 61 72 2E 74 78 74 20 7B 46 20 33 33 20 35 33 31 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 2D 5C 7D 2D 5C 7D 2D 62 72 61 63 6B 65 74 2D 66 61 72 32 2D 6F 70 70 6F 73 69 74 65 2E 74 78 74 20 7B 46 20 34 39 20 34 39 7D 20 69 2D 68 61 76 65 2D 6F 6E 65 2D 5C 7B 2D 62 72 61 63 6B 65 74 2E 74 78 74 20 7B 46 20 32 37 20 31 30 38 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 5C 7D 2D 5C 7D 2D 62 72 61 63 6B 65 74 2D 66 61 72 31 2D 6F 70 70 6F 73 69 74 65 2E 74 78 74 20 7B 46 20 34 39 20 32 36 30 7D 20 7B 7B 2D 69 2D 61 6D 2D 73 75 72 72 6F 75 6E 64 65 64 2D 77 69 74 68 2D 62 72 61 63 6B 65 74 73 2E 74 78 74 2D 7D 7D 20 7B 46 20 33 30 20 38 32 31 7D 20 69 2D 68 61 76 65 2D 6F 70 65 6E 2D 7B 2D 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2D 66 61 72 2E 74 78 74 20 7B 46 20 34 33 20 37 33 38 7D 20 69 2D 68 61 76 65 2D 6F 6E 65 2D 5C 7D 2D 62 72 61 63 6B 65 74 2E 74 78 74 20 7B 46 20 32 37 20 32 38 37 7D 20 69 2D 68 61 76 65 2D 6F 70 65 6E 2D 7B 2D 61 6E 64 2D 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2E 74 78 74 20 7B 46 20 33 39 20 34 34 38 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 6F 70 65 6E 2D 7B 7B 7D 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2D 61 64 6A 61 63 65 6E 74 2D 6E 65 73 74 65 64 2E 74 78 74 20 7B 46 20 35 35 20 33 34 32 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 2D 5C 7B 2D 5C 7D 2D 62 72 61 63 6B 65 74 2D 66 61 72 32 2E 74 78 74 20 7B 46 20 34 30 20 32 31 31 7D 20 69 2D 68 61 76 65 2D 74 77 6F 2D 6F 70 65 6E 2D 7B 2D 7B 7D 2D 7D 2D 62 72 61 63 6B 65 74 2D 70 61 69 72 2D 66 61 72 2D 6E 65 73 74 65 64 2E 74 78 74 20 7B 46 20 35 30 20 34 39 38 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 5C 7B 5C 7D 2D 62 72 61 63 6B 65 74 2D 6E 65 61 72 2E 74 78 74 20 7B 46 20 34 30 20 31 37 31 7D 20 69 2D 68 61 76 65 2D 75 6E 62 61 6C 61 6E 63 65 64 2D 5C 7B 2D 5C 7B 5C 7D 2D 62 72 61 63 6B 65 74 2D 66 61 72 31 2E 74 78 74 20 7B 46 20 34 30 20 34 30 39 7D"
)
big = big_bytes.decode()
print(big)
print(toc_parser.parse(big))
