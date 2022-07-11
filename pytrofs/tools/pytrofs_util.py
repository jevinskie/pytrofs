#!/usr/bin/env python3

import argparse

from pytrofs import trofs


def real_main(args):
    print(args)
    if args.extract:
        trofs.extract(args.trofs, args.directory)
    elif args.create:
        trofs.create(args.trofs, args.directory)
    else:
        raise ValueError("Must choose --extract or --create")


def main():
    parser = argparse.ArgumentParser(description="pytrofs-util")
    op = parser.add_mutually_exclusive_group()
    op.add_argument(
        "-x", "--extract", action="store_true", help="Extract trofs archive to directory."
    )
    op.add_argument(
        "-c", "--create", action="store_true", help="Create trofs archive from directory."
    )
    parser.add_argument("-d", "--dir", required=True, dest="directory", help="Directory.")
    parser.add_argument("-t", "--trofs", required=True, help="trofs archive.")
    args = parser.parse_args()
    real_main(args)


if __name__ == "__main__":
    main()
