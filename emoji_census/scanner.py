"""Group a stream of characters into emoji sequences.

An emoji as a person sees it is often several Unicode codepoints: a base
pictograph, an optional skin tone modifier, an optional variation
selector, and possibly a chain of zero-width-joined pieces (a family, a
profession, a couple). Flags are a pair of regional indicators. Keycaps
are a digit or symbol plus a combining enclosing keycap mark. Counting
codepoints one at a time fragments all of this; this module reassembles
it before anything gets tallied.

The input is any iterable of single characters, not a string. That is
what lets the caller feed it a generator that reads a file in fixed-size
chunks instead of a string holding the whole file.
"""

from collections import deque

from . import ranges


class _Peekable:
    """Wraps an iterator with lookahead, buffering only what's been peeked."""

    def __init__(self, iterator):
        self._it = iter(iterator)
        self._buffer = deque()

    def peek(self, offset=0):
        while len(self._buffer) <= offset:
            try:
                self._buffer.append(next(self._it))
            except StopIteration:
                return None
        return self._buffer[offset]

    def __next__(self):
        if self._buffer:
            return self._buffer.popleft()
        return next(self._it)

    def __iter__(self):
        return self


def _consume_flag(first, stream):
    """A regional indicator, optionally paired with a second one."""
    seq = first
    nxt = stream.peek()
    if nxt is not None and ranges.is_regional_indicator(ord(nxt)):
        seq += next(stream)
    return seq


def _consume_keycap(first, stream):
    """digit/#/* + optional FE0F + required combining keycap mark."""
    has_vs = stream.peek(0) == "\N{VARIATION SELECTOR-16}"
    combiner_offset = 1 if has_vs else 0
    if stream.peek(combiner_offset) != chr(ranges.KEYCAP_COMBINER):
        return first
    seq = first
    if has_vs:
        seq += next(stream)
    seq += next(stream)
    return seq


def _consume_pictograph(first, stream):
    """Base pictograph plus any modifiers and ZWJ-joined continuations."""
    seq = first
    while True:
        nxt = stream.peek(0)
        if nxt is None:
            break
        cp = ord(nxt)

        if cp == ranges.VARIATION_SELECTOR_16:
            seq += next(stream)
            continue

        if ranges.SKIN_TONE_START <= cp <= ranges.SKIN_TONE_END:
            seq += next(stream)
            continue

        if cp == ranges.ZERO_WIDTH_JOINER:
            after = stream.peek(1)
            if after is not None and ranges.is_emoji_base(ord(after)):
                seq += next(stream)  # the ZWJ itself
                seq += next(stream)  # the joined base it introduces
                continue
            break

        if ranges.TAG_START <= cp <= ranges.TAG_END:
            seq += next(stream)
            if cp == ranges.TAG_TERMINATOR:
                break
            continue

        break
    return seq


def iter_sequences(chars):
    """Yield emoji sequences found in `chars`, an iterable of single characters.

    Non-emoji characters are skipped without buffering: memory use is
    bounded by the length of the longest emoji sequence encountered, not
    by the size of the input.
    """
    stream = _Peekable(chars)
    for ch in stream:
        cp = ord(ch)

        if ranges.is_regional_indicator(cp):
            yield _consume_flag(ch, stream)
            continue

        if ranges.is_keycap_base(cp):
            seq = _consume_keycap(ch, stream)
            if seq != ch:
                yield seq
            continue

        if ranges.is_emoji_base(cp):
            yield _consume_pictograph(ch, stream)
            continue
