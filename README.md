# emoji-census

Count how often each emoji *sequence* appears in some text.

## the problem

Most emoji you actually type aren't a single codepoint. A thumbs-up with a
skin tone is two codepoints. A family is a chain of people joined by
zero-width joiners. A flag is a pair of regional indicator letters. A
keycap like 5️⃣ is a digit plus a variation selector plus a combining
enclosing keycap mark. If you count Unicode codepoints one at a time, all
of that gets shredded: the family emoji turns into five unrelated tallies
for "man", "woman", "girl", "boy", and a joiner nobody cares about.

`emoji-census` walks the input character by character and reassembles
these sequences using the actual grammar (ZWJ chains, skin tone
modifiers, regional indicator pairs, keycaps, tag sequences for
subdivision flags) before counting anything. What you get out is a tally
of the things a person would say they typed, not a tally of code units.

It also treats the input as a stream. Chat exports and social media
dumps can be gigabytes; this tool never reads more than a fixed-size
chunk into memory at once, so scanning a 10 MB file and a 10 GB file use
the same amount of RAM.

## usage

```
$ python -m emoji_census.cli chat_log.txt
41      👍🏽    U+1F44D U+1F3FD
19      👨‍👩‍👧‍👦    U+1F468 U+200D U+1F469 U+200D U+1F467 U+200D U+1F466
12      🇨🇦    U+1F1E8 U+1F1E6
7       5️⃣     U+0035 U+FE0F U+20E3
```

Reading from stdin works the same way:

```
$ cat chat_log.txt | python -m emoji_census.cli
```

Scan several files at once (each is opened and streamed in turn, so only
one file's chunk buffer is ever in memory):

```
$ python -m emoji_census.cli 2023.txt 2024.txt 2025.txt
```

Limit output to the most common sequences:

```
$ python -m emoji_census.cli -n 10 huge_corpus.txt
```

Some emoji have both a text-style and an emoji-style presentation that
only differ by a trailing variation selector-16 -- the same umbrella
comes out as either `☂` or `☂️` depending on what typed it. `--normalize`
strips that selector before counting so the two presentations tally as
one sequence instead of splitting the count:

```
$ python -m emoji_census.cli --normalize chat_log.txt
```

Output is tab-separated: count, the sequence itself, then its codepoints
in `U+XXXX` form (useful when your terminal or font can't render
something, or when you need to paste an exact sequence somewhere else).

For machine-readable output, pass `--json`:

```
$ python -m emoji_census.cli --json chat_log.txt
[
  {
    "sequence": "👍🏽",
    "count": 41,
    "codepoints": ["U+1F44D", "U+1F3FD"]
  },
  ...
]
```

## installing

No third-party dependencies -- the standard library is enough. To get the
`emoji-census` command on your PATH:

```
$ pip install -e .
$ emoji-census chat_log.txt
```

Or just run it as a module without installing anything:

```
$ python -m emoji_census.cli chat_log.txt
```

## how the sequence grammar is approximated

`emoji_census/ranges.py` lists the Unicode blocks and combining
characters involved (pictograph ranges, regional indicators, skin tone
modifiers, the ZWJ, variation selector 16, keycap combiner, tag
characters). This is a hand-picked approximation of "things people use as
emoji," not a load of the official `emoji-data.txt` table from
unicode.org -- pulling that in would mean a network fetch and a versioned
copy on disk, which felt like more machinery than a first version needs.
It covers the sequences you'll actually run into; see the roadmap for
where it falls short.

## license

MIT, see LICENSE.
