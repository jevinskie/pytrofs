#!/usr/bin/env tclsh

package require Tcl 8.6
package require cmdline 1.5
package require trofs

namespace import trofs::*

set options {
    {c "create a trofs archive"}
    {x "extract a trofs archive"}
    {f "force overwriting output path"}
    {i.arg "" "input directory or trofs archive"}
    {o.arg "" "output directory or trofs archive"}
}

set usage ": trofs-util \[options]\noptions:"


try {
    array set params [::cmdline::getoptions argv $options $usage]
    # Note: argv is modified now. The recognized options are
    # removed from it, leaving the non-option arguments behind.
} trap {CMDLINE USAGE} {msg o} {
    # Trap the usage signal, print the message, and exit the application.
    # Note: Other errors are not caught and passed through to higher levels!
    puts $msg
    exit 1
}

parray params

if {([llength argv] != 0) && ($argv != "")} {
    puts "Extra arguments '$argv' detected"
    exit 1
}
if {$params(i) eq ""} {
    puts "Must provide an input path with -i <path>"
    exit 1
} elseif {$params(o) eq ""} {
    puts "Must provide an output path with -o <path>"
    exit 1
}
if {!($params(c) ^ $params(x))} {
    puts "Must specify one of -x or -c but not both"
    exit 1
}

if {![file exists $params(i)]} {
    if {$params(c) && ![file isdirectory $params(i)]} {
        puts "When compressing, input path ('$params(i)') must be a directory"
        exit 1
    }
}

if {[file exists $params(o)] && !$params(f)} {
    puts "Cowardly refusinig to overwrite output path '$params(o)'"
} else {
    file delete -force $params(o)
}

set abs_out [file normalize $params(o)]

if {$params(c)} {
    cd [file dirname $params(i)]
    archive [file tail $params(i)] $abs_out
} else {
    set mounted_dir [mount $params(i)]
    file copy $mounted_dir $abs_out
    unmount $mounted_dir
}
