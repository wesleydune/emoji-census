import argparse
import collections
import json
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


def _codepoint_names(sequence):
    return ["U+%04X" % ord(c) for c in sequence]


def _format_row(sequence, count):
    codepoints = " ".join(_codepoint_names(sequence))
    return "%d\t%s\t%s" % (count, sequence, codepoints)


def _format_json(tally, top):
    rows = [
        {"sequence": sequence, "count": count, "codepoints": _codepoint_names(sequence)}
        for sequence, count in tally.most_common(top)
    ]
    return json.dumps(rows, ensure_ascii=False, indent=2)


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
    parser.add_argument(
        "--json",
        action="store_true",
        help="print results as a JSON array instead of tab-separated rows",
    )
    args = parser.parse_args(argv)

    tally = collections.Counter()
    for fileobj in _open_inputs(args.paths):
        for sequence in scanner.iter_sequences(_char_stream(fileobj)):
            tally[sequence] += 1

    if args.json:
        print(_format_json(tally, args.top))
    else:
        for sequence, count in tally.most_common(args.top):
            print(_format_row(sequence, count))

    return 0


if __name__ == "__main__":
    sys.exit(main())
