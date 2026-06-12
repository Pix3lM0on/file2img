"""Command line interface."""

from __future__ import annotations

import argparse

from .codec import decode_file, encode_file
from .patterns import available_patterns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="file2img")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="convert a file into an image")
    encode_parser.add_argument("input")
    encode_parser.add_argument("output")
    encode_parser.add_argument(
        "--pattern",
        choices=available_patterns(),
        default="spiral",
        help="pixel pattern to use",
    )

    decode_parser = subparsers.add_parser("decode", help="convert a file2img image back into a file")
    decode_parser.add_argument("input")
    decode_parser.add_argument("output", nargs="?")

    args = parser.parse_args(argv)

    if args.command == "encode":
        encode_file(args.input, args.output, args.pattern)
        print(f"encoded {args.input} -> {args.output}")
        return 0

    if args.command == "decode":
        output = decode_file(args.input, args.output)
        print(f"decoded {args.input} -> {output}")
        return 0

    parser.error("unknown command")
    return 2
