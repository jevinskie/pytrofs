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
gen_intgen fidx

array set fnames {}

proc add_f {fid name} {
    upvar fnames fnames
    set fnames($fid) [list $name [fidx_intgen]]
}

proc get_fid_and_fname_by_fidx {fidx} {
    upvar fnames fnames
    foreach {fid v} [array get fnames] {
        set cur_fname [lindex $v 0]
        set cur_fidx [lindex $v 1]
        if [expr $fidx == $cur_fidx] {
            return [list $fid $cur_fname]
        }
    }
    return -1
}

add_f fnospace "hello-world.txt"
add_f fnospacebare hello-world.txt
add_f fspace "hello world.txt"
add_f fquote "hello-\"-world.txt"
add_f fbbraces "{hello-world.txt}"
add_f fbbracesmobrace "{hello-{-world.txt}"
add_f fbbracesmcbrace "{hello-{-world.txt}"
add_f fbbracesspace "{hello world.txt}"
add_f fmbrace "hello-{-world.txt"
add_f fmbraces "hello-{}-world.txt"
add_f fsobrace "{hello-world.txt"
add_f fscbrace "}hello-world.txt"
add_f feobrace "hello-world.txt{"
add_f fecbrace "hello-world.txt}"
add_f funicode "ä-\"-b.txt"
add_f fbspace " hello-world.txt"
add_f fbspacemobrace " hello-{-world.txt"
add_f fbspacemcbrace " hello-}-world.txt"
add_f fespace "hello-world.txt "
add_f fespacemobrace "hello-{-world.txt "
add_f fespacemcbrace "hello-}-world.txt "
add_f faspacemobrace " hello-{-world.txt "
add_f faspacemcbrace " hello-}-world.txt "
add_f faspacemabrace " hello-{}-world.txt "
add_f fnewline "hello\nworld.txt"
add_f fnewlinequote "hello-newline-\n-quote-\"-world.txt"
add_f fempty ""
add_f fhash "#"
add_f fhashfirst "#hai"
add_f fhashmiddle "hai#2u"
add_f fhashend "hai#"
add_f fhashbrace "#{a\"b}"
add_f fnohashbrace "{a\"b}"

array set fcontents {}
foreach {fid v} [array get fnames] {
    set cur_fname [lindex $v 0]
    set cur_fidx [lindex $v 1]
    set fcontents($fid) "contents of fid: $fid fname: $cur_fname fidx: $cur_fidx\n"
}

parray fcontents

proc get_content_for_fid {fid} {
    upvar fcontents fcontents
    return $fcontents($fid)
}

set first_fidx 1
set last_fidx [expr [fidx_intgen] - 1]
set num_fidx [expr $last_fidx - $first_fidx]

set content ""
set cur_off 1
for {set fidx $first_fidx} {$fidx < $last_fidx} {incr fidx} {
    set fid [lindex [get_fid_and_fname_by_fidx $fidx] 0]
    set content "$content[get_content_for_fid $fid]"
}

proc fp {fid} {
    upvar fcontents fcontents
    set content [get_content_for_fid $fid]
    set len [string length [encoding convertto utf-8 $content]]
    return [list F $len [off_intgen]]
}

proc lp {tgt} {
    return [list L $tgt]
}

array set toc {}

foreach {fid finfo} [array get fnames] {
    set fname [lindex $finfo 0]
    set fidx [lindex $finfo 1]
    puts "pee fid: $fid fname $fname"
    set toc($fname) [fp $fid]
    set symlink_name "$fname-symlink"
    set toc($symlink_name) [lp $fname]
}

parray toc
puts [array get toc]

set ftoc [open $test_toc_fname w]
fconfigure $ftoc -encoding binary
write $ftoc \u001A
fconfigure $ftoc -encoding utf-8
write $ftoc $content
write $ftoc [array get toc]
fconfigure $ftoc -translation binary
write $ftoc [binary format I 0xDEADBEEF]
close $ftoc
