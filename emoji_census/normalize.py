"""Normalize assembled sequences so comparable emoji tally together.

Some emoji have a text-style default presentation and only render as a
colorful pictograph because of a trailing variation selector-16 (U+FE0F).
People are inconsistent about typing it -- the same umbrella comes out as
either "☂" or "☂️" depending on the keyboard or client that
produced it -- so counting the raw sequences splits what a person would
call one emoji into two rows. Stripping the selector before tallying
merges those back together.
"""

VARIATION_SELECTOR_16 = "\N{VARIATION SELECTOR-16}"


def strip_variation_selectors(sequence):
    """Return `sequence` with all variation selector-16 characters removed.

    Skin tone modifiers, ZWJ joins, flags, and keycaps are left untouched;
    only the presentation-style selector is stripped, since that's the
    only piece that varies without changing what emoji a person meant.
    """
    if VARIATION_SELECTOR_16 not in sequence:
        return sequence
    return sequence.replace(VARIATION_SELECTOR_16, "")
