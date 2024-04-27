#!/usr/bin/env tclsh

interp alias {} write {} puts -nonewline

proc intgen {{i 0}} {
  proc intgen "{i [incr i]}" [info body intgen]
  return $i
}

proc fp {} {
    return [list F 42 [intgen]]
}

set fnospace "hello-world.txt"
set fnospacebare hello-world.txt
set fspace "hello world.txt"
set fquote "hello-\"-world.txt"
set fbbraces "{hello-world.txt}"
set fbbracesmobrace "{hello-{-world.txt}"
set fbbracesmcbrace "{hello-{-world.txt}"
set fbbracesspace "{hello world.txt}"
set fmbrace "hello-{-world.txt"
set fmbraces "hello-{}-world.txt"
set fsobrace "{hello-world.txt"
set fscbrace "}hello-world.txt"
set feobrace "hello-world.txt{"
set fecbrace "hello-world.txt}"
set funicode "ä-\"-b.txt"
set fbspace " hello-world.txt"
set fbspacemobrace " hello-{-world.txt"
set fbspacemcbrace " hello-}-world.txt"
set fespace "hello-world.txt "
set fespacemobrace "hello-{-world.txt "
set fespacemcbrace "hello-}-world.txt "
set faspacemobrace " hello-{-world.txt "
set faspacemcbrace " hello-}-world.txt "
set faspacemabrace " hello-{}-world.txt "
set fnewline "hello\nworld.txt"
set fnewlinequote "hello-newline-\n-quote-\"-world.txt"
set fempty ""

array set idx {}

set idx($fnospace) [fp]
set idx($fnospacebare) [fp]
set idx($fspace) [fp]
set idx($fquote) [fp]
set idx($fbbraces) [fp]
set idx($fbbracesmobrace) [fp]
set idx($fbbracesmcbrace) [fp]
set idx($fbbracesspace) [fp]
set idx($fmbrace) [fp]
set idx($fmbraces) [fp]
set idx($fsobrace) [fp]
set idx($fscbrace) [fp]
set idx($feobrace) [fp]
set idx($fecbrace) [fp]
set idx($funicode) [fp]
set idx($fbspace) [fp]
set idx($fbspacemobrace) [fp]
set idx($fbspacemcbrace) [fp]
set idx($fespace) [fp]
set idx($fespacemobrace) [fp]
set idx($fespacemcbrace) [fp]
set idx($faspacemobrace) [fp]
set idx($faspacemcbrace) [fp]
set idx($faspacemabrace) [fp]
set idx($fnewline) [fp]
set idx($fnewlinequote) [fp]
set idx($fempty) [fp]

puts $fnewlinequote
puts [array get idx]
