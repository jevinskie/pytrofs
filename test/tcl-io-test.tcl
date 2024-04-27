#!/usr/bin/env tclsh

interp alias {} write {} puts -nonewline

set fnospace "hello-world.txt"
set fnospacebare hello-world.txt
set fspace "hello world.txt"
set fquote "hello-\"-world.txt"
set fbbraces "{hello-world.txt}"
set fbbracesspace "{hello world.txt}"
set fmbrace "hello-{-world.txt"
set fsobrace "{hello-world.txt"
set fscbrace "}hello-world.txt"
set feobrace "hello-world.txt{"
set fecbrace "hello-world.txt}"
set funicode "ä-\"-b.txt"

set fp [list F 42 243]

array set idx {}

set idx($fnospace) $fp
set idx($fnospacebare) $fp
set idx($fspace) $fp
set idx($fquote) $fp
set idx($fbbraces) $fp
set idx($fbbracesspace) $fp
set idx($fmbrace) $fp
set idx($fsobrace) $fp
set idx($fscbrace) $fp
set idx($feobrace) $fp
set idx($fecbrace) $fp
set idx($funicode) $fp

write [array get idx]
