"""Tests for emoji_census.normalize."""

import unittest

from emoji_census import ranges
from emoji_census.normalize import strip_variation_selectors


class StripVariationSelectorsTests(unittest.TestCase):
    def test_leaves_sequence_without_a_selector_unchanged(self):
        umbrella = "☂"
        self.assertEqual(strip_variation_selectors(umbrella), umbrella)

    def test_strips_trailing_selector(self):
        umbrella_text_style = "☂"
        umbrella_emoji_style = "☂" + chr(ranges.VARIATION_SELECTOR_16)
        self.assertEqual(
            strip_variation_selectors(umbrella_emoji_style), umbrella_text_style
        )

    def test_strips_selector_in_the_middle_of_a_zwj_chain(self):
        with_selector = (
            "❤" + chr(ranges.VARIATION_SELECTOR_16)
            + chr(ranges.ZERO_WIDTH_JOINER)
            + "\U0001F525"
        )
        without_selector = "❤" + chr(ranges.ZERO_WIDTH_JOINER) + "\U0001F525"
        self.assertEqual(strip_variation_selectors(with_selector), without_selector)

    def test_leaves_skin_tones_and_flags_untouched(self):
        thumbs_up_medium = "\U0001F44D" + chr(ranges.SKIN_TONE_START + 2)
        self.assertEqual(strip_variation_selectors(thumbs_up_medium), thumbs_up_medium)


if __name__ == "__main__":
    unittest.main()
