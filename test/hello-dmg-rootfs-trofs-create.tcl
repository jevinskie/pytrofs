#!/usr/bin/env tclsh

package require trofs
namespace import trofs::*

set dirname [file dirname [info script]]
archive [file join $dirname hello_dmg_rootfs] [file join $dirname hello_dmg_rootfs.trofs]
