#!/usr/bin/env python3

import argparse
import logging
import sys

from packaging.version import Version
from rich.console import Console
from rich.logging import RichHandler

from .. import _version, trofs

LOG_FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING,
    format=LOG_FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
)

program_name = "pytrofs-util"

log = logging.getLogger(program_name)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=program_name)
    op = parser.add_mutually_exclusive_group()
    op.add_argument(
        "-x", "--extract", action="store_true", help="Extract trofs archive to directory."
    )
    op.add_argument(
        "-c", "--create", action="store_true", help="Create trofs archive from directory."
    )
    parser.add_argument(
        "-d", "--dir", required=True, dest="directory", help="Input/output directory."
    )
    parser.add_argument("-t", "--trofs", required=True, help="Input/output trofs archive.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s version: {Version(_version.version)}",
    )
    return parser


def real_main(args: argparse.Namespace) -> int:
    if args.extract:
        trofs.extract(args.trofs, args.directory)
    elif args.create:
        trofs.create(args.trofs, args.directory)
    else:
        raise ValueError("Must choose --extract or --create")
    return 0


def main() -> int:
    try:
        return real_main(get_arg_parser().parse_args())
    except Exception:
        log.exception(f"Received an unexpected exception when running {program_name}")
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
