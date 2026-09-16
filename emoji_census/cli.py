import argparse
import collections
import sys

from . import scanner

CHUNK_SIZE = 1 << 16  # 64 KiB of text per read, regardless of file size


def _char_stream(fileobj, chunk_size=CHUNK_SIZE):
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            return
        for ch in chunk:
            yield ch


def _open_inputs(paths):
    if not paths:
        yield sys.stdin
        return
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as fileobj:
            yield fileobj


def _format_row(sequence, count):
    codepoints = " ".join("U+%04X" % ord(c) for c in sequence)
    return "%d\t%s\t%s" % (count, sequence, codepoints)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emoji-census",
        description=(
            "Count emoji sequences (not raw codepoints) in text. "
            "Reads files or stdin as a stream, so input size doesn't "
            "translate into memory use."
        ),
    )
    parser.add_argument(
        "paths", nargs="*", metavar="FILE", help="files to scan (default: stdin)"
    )
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="only show the N most common sequences",
    )
    args = parser.parse_args(argv)

    tally = collections.Counter()
    for fileobj in _open_inputs(args.paths):
        for sequence in scanner.iter_sequences(_char_stream(fileobj)):
            tally[sequence] += 1

    for sequence, count in tally.most_common(args.top):
        print(_format_row(sequence, count))

    return 0


if __name__ == "__main__":
    sys.exit(main())
