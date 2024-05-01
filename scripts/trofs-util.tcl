#!/usr/bin/env tclsh

package require Tcl 8.6
package require cmdline 1.5
package require trofs

namespace import trofs::*

set options {
    {c "create a trofs archive"}
    {x "extract a trofs archive"}
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

puts "argv: $argv"
parray params

# archive hello_dmg_rootfs hello_dmg_rootfs.trofs
