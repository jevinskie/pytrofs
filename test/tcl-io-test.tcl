#!/usr/bin/env tclsh

interp alias {} write {} puts -nonewline


proc intgen {{i 0}} {
    proc intgen "{i [incr i]}" [info body intgen]
    return $i
}

proc gen_intgen {name} {
    proc "${name}_intgen" {{i -1}} {
        proc [dict get [info frame 0] proc] "{i [incr i]}" [info body [dict get [info frame 0] proc]]
        return $i
    }
}

gen_intgen off_gen
gen_intgen jgen


proc fp {} {
    return [list F 1 [intgen]]
}
proc lp {tgt} {
    return [list L $tgt]
}

array set fnames {}

proc add_fname {id {name}} {
    upvar fnames local_fnames
    set local_fnames($id) $name
    parray local_fnames
}

add_fname fnospace "hello-world.txt"
add_fname fnospacebare hello-world.txt
add_fname fspace "hello world.txt"
add_fname fquote "hello-\"-world.txt"
add_fname fbbraces "{hello-world.txt}"
add_fname fbbracesmobrace "{hello-{-world.txt}"
add_fname fbbracesmcbrace "{hello-{-world.txt}"
add_fname fbbracesspace "{hello world.txt}"
add_fname fmbrace "hello-{-world.txt"
add_fname fmbraces "hello-{}-world.txt"
add_fname fsobrace "{hello-world.txt"
add_fname fscbrace "}hello-world.txt"
add_fname feobrace "hello-world.txt{"
add_fname fecbrace "hello-world.txt}"
add_fname funicode "ä-\"-b.txt"
add_fname fbspace " hello-world.txt"
add_fname fbspacemobrace " hello-{-world.txt"
add_fname fbspacemcbrace " hello-}-world.txt"
add_fname fespace "hello-world.txt "
add_fname fespacemobrace "hello-{-world.txt "
add_fname fespacemcbrace "hello-}-world.txt "
add_fname faspacemobrace " hello-{-world.txt "
add_fname faspacemcbrace " hello-}-world.txt "
add_fname faspacemabrace " hello-{}-world.txt "
add_fname fnewline "hello\nworld.txt"
add_fname fnewlinequote "hello-newline-\n-quote-\"-world.txt"
add_fname fempty ""
add_fname fhash "#"
add_fname fhashfirst "#hai"
add_fname fhashmiddle "hai#2u"
add_fname fhashend "hai#"
add_fname fhashbrace "#{a\"b}"
add_fname fnohashbrace "{a\"b}"

puts "fnames begin:"
parray fnames
puts "fnames end"

# # add_fname k ""
# # set v ""
# array for {{k} {v}} fnames {
#     puts "fnames\[$k\] = $v"
# }

# puts "fnames: [dict get fnames]"

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
set fhash "#"
set fhashfirst "#hai"
set fhashmiddle "hai#2u"
set fhashend "hai#"
set fhashbrace "#{a\"b}"
set fnohashbrace "{a\"b}"


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
set idx($fhash) [fp]
set idx($fhashfirst) [fp]
set idx($fhashmiddle) [fp]
set idx($fhashend) [fp]
set idx($fhashbrace) [fp]
set idx($fnohashbrace) [fp]

parray idx
puts [array get idx]
