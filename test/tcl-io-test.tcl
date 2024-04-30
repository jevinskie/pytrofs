#!/usr/bin/env tclsh

interp alias {} write {} puts -nonewline

set dirname [file dirname [info script]]
set test_toc_fname [file join $dirname test-toc.toc]
file delete $test_toc_fname

proc gen_intgen {name} {
    proc "${name}_intgen" {{i 0}} {
        proc [dict get [info frame 0] proc] "{i [incr i]}" [info body [dict get [info frame 0] proc]]
        return $i
    }
}

gen_intgen off

proc fp {} {
    return [list F 1 [off_intgen]]
}
proc lp {tgt} {
    return [list L $tgt]
}

array set fnames {}

proc add_fname {id {name}} {
    upvar fnames local_fnames
    set local_fnames($id) $name
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

array set toc {}

foreach {k v} [array get fnames] {
    set fp_info [fp]
    set toc($v) [fp]
    puts "symlink: [expr [lindex $fp_info 2]]-symlink -> $v"
    set toc("[expr [lindex $fp_info 2]]-symlink") [lp $v]
}

parray toc
puts [array get toc]

set ftoc [open $test_toc_fname w]
fconfigure $ftoc -encoding binary
write $ftoc \u001A
fconfigure $ftoc -encoding utf-8
write $ftoc [array get toc]
fconfigure $ftoc -translation binary
write $ftoc \u001A
write $ftoc [binary format I 0xDEADBEEF]
close $ftoc
