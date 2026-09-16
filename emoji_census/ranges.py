"""Codepoint ranges and combining characters used to assemble emoji sequences.

This is a hand-picked approximation of the emoji-relevant blocks of Unicode,
not a load of the official emoji-data.txt table (that needs a network fetch
and a versioned copy on disk, which is future work -- see README). It is
good enough to find the vast majority of emoji people actually type: the
core pictograph blocks, the older dingbat-era symbols that got promoted to
emoji, flags, skin tones, and ZWJ-joined sequences.
"""

# (start, end) inclusive, single codepoints that can begin or stand alone as
# an emoji outside the big supplementary-plane blocks below.
EMOJI_RANGES = (
    (0x203C, 0x203C),
    (0x2049, 0x2049),
    (0x2122, 0x2122),
    (0x2139, 0x2139),
    (0x2194, 0x21AA),
    (0x231A, 0x231B),
    (0x2328, 0x2328),
    (0x23CF, 0x23CF),
    (0x23E9, 0x23FA),
    (0x24C2, 0x24C2),
    (0x25AA, 0x25FE),
    (0x2600, 0x27BF),
    (0x2934, 0x2935),
    (0x2B05, 0x2B07),
    (0x2B1B, 0x2B1C),
    (0x2B50, 0x2B50),
    (0x2B55, 0x2B55),
    (0x3030, 0x3030),
    (0x303D, 0x303D),
    (0x3297, 0x3297),
    (0x3299, 0x3299),
    # Covers Miscellaneous Symbols and Pictographs, Emoticons, Transport and
    # Map Symbols, Supplemental Symbols and Pictographs, Symbols and
    # Pictographs Extended-A, and the odd non-emoji neighbor block along
    # the way (mahjong tiles, chess symbols). Treated as emoji-ish for now.
    (0x1F000, 0x1FFFF),
)

VARIATION_SELECTOR_16 = 0xFE0F
ZERO_WIDTH_JOINER = 0x200D

SKIN_TONE_START = 0x1F3FB
SKIN_TONE_END = 0x1F3FF

REGIONAL_INDICATOR_START = 0x1F1E6
REGIONAL_INDICATOR_END = 0x1F1FF

KEYCAP_COMBINER = 0x20E3
KEYCAP_BASES = frozenset(
    [ord(c) for c in "0123456789#*"]
)

# Tag characters used for subdivision flags such as England/Scotland/Wales,
# e.g. black flag + tag letters + TAG_TERMINATOR.
TAG_START = 0xE0020
TAG_END = 0xE007F
TAG_TERMINATOR = 0xE007F


def is_emoji_base(codepoint):
    return any(start <= codepoint <= end for start, end in EMOJI_RANGES)


def is_regional_indicator(codepoint):
    return REGIONAL_INDICATOR_START <= codepoint <= REGIONAL_INDICATOR_END


def is_keycap_base(codepoint):
    return codepoint in KEYCAP_BASES
