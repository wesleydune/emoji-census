"""Edge cases for the sequence grammar in emoji_census.scanner.

Each test builds its input from explicit codepoints rather than pasting
emoji literals, so it's obvious from the test itself which characters are
supposed to join together and which aren't.
"""

import unittest

from emoji_census import ranges
from emoji_census.scanner import iter_sequences


def seq(*codepoints):
    return "".join(chr(cp) for cp in codepoints)


class SimplePictographTests(unittest.TestCase):
    def test_single_codepoint_emoji_stands_alone(self):
        grinning_face = seq(0x1F600)
        self.assertEqual(list(iter_sequences(grinning_face)), [grinning_face])

    def test_variation_selector_attaches_to_its_base(self):
        umbrella = seq(0x2602, ranges.VARIATION_SELECTOR_16)
        self.assertEqual(list(iter_sequences(umbrella)), [umbrella])

    def test_plain_text_around_an_emoji_is_dropped(self):
        text = "hi " + seq(0x1F600) + " there"
        self.assertEqual(list(iter_sequences(text)), [seq(0x1F600)])

    def test_two_pictographs_back_to_back_stay_separate(self):
        text = seq(0x1F600) + seq(0x1F601)
        self.assertEqual(list(iter_sequences(text)), [seq(0x1F600), seq(0x1F601)])

    def test_empty_input_yields_nothing(self):
        self.assertEqual(list(iter_sequences("")), [])


class SkinToneTests(unittest.TestCase):
    def test_skin_tone_modifier_attaches_to_base(self):
        thumbs_up_medium = seq(0x1F44D, ranges.SKIN_TONE_START + 2)
        self.assertEqual(list(iter_sequences(thumbs_up_medium)), [thumbs_up_medium])

    def test_skin_tone_modifier_with_no_base_is_dropped(self):
        lone_modifier = seq(ranges.SKIN_TONE_START)
        self.assertEqual(list(iter_sequences(lone_modifier)), [])


class ZwjChainTests(unittest.TestCase):
    def test_four_person_family_is_one_sequence(self):
        family = seq(
            0x1F468,
            ranges.ZERO_WIDTH_JOINER,
            0x1F469,
            ranges.ZERO_WIDTH_JOINER,
            0x1F467,
            ranges.ZERO_WIDTH_JOINER,
            0x1F466,
        )
        self.assertEqual(list(iter_sequences(family)), [family])

    def test_joiner_followed_by_non_emoji_breaks_the_chain(self):
        text = seq(0x1F468, ranges.ZERO_WIDTH_JOINER) + "x"
        self.assertEqual(list(iter_sequences(text)), [seq(0x1F468)])

    def test_joiner_at_end_of_stream_breaks_the_chain(self):
        text = seq(0x1F468, ranges.ZERO_WIDTH_JOINER)
        self.assertEqual(list(iter_sequences(text)), [seq(0x1F468)])


class FlagTests(unittest.TestCase):
    def test_regional_indicator_pair_is_one_flag(self):
        canada = seq(0x1F1E8, 0x1F1E6)
        self.assertEqual(list(iter_sequences(canada)), [canada])

    def test_lone_regional_indicator_at_end_of_stream_stands_alone(self):
        lone = seq(0x1F1E8)
        self.assertEqual(list(iter_sequences(lone)), [lone])

    def test_adjacent_flags_do_not_merge_into_one_sequence(self):
        canada = seq(0x1F1E8, 0x1F1E6)
        usa = seq(0x1F1FA, 0x1F1F8)
        self.assertEqual(list(iter_sequences(canada + usa)), [canada, usa])


class KeycapTests(unittest.TestCase):
    def test_keycap_with_variation_selector(self):
        five = seq(ord("5"), ranges.VARIATION_SELECTOR_16, ranges.KEYCAP_COMBINER)
        self.assertEqual(list(iter_sequences(five)), [five])

    def test_keycap_without_variation_selector(self):
        five = seq(ord("5"), ranges.KEYCAP_COMBINER)
        self.assertEqual(list(iter_sequences(five)), [five])

    def test_bare_digit_without_combiner_is_not_a_sequence(self):
        self.assertEqual(list(iter_sequences("5")), [])

    def test_digit_with_variation_selector_but_no_combiner_is_dropped(self):
        text = seq(ord("5"), ranges.VARIATION_SELECTOR_16) + "x"
        self.assertEqual(list(iter_sequences(text)), [])


class TagSequenceTests(unittest.TestCase):
    def test_subdivision_flag_tag_sequence_is_one_sequence(self):
        # England: black flag + tag letters "gbeng" + tag terminator.
        england = seq(
            0x1F3F4,
            0xE0067,
            0xE0062,
            0xE0065,
            0xE006E,
            0xE0067,
            ranges.TAG_TERMINATOR,
        )
        self.assertEqual(list(iter_sequences(england)), [england])

    def test_unterminated_tag_sequence_is_consumed_up_to_end_of_stream(self):
        truncated = seq(0x1F3F4, 0xE0067, 0xE0062)
        self.assertEqual(list(iter_sequences(truncated)), [truncated])


class StreamingInputTests(unittest.TestCase):
    def test_accepts_any_iterable_of_characters_not_just_a_string(self):
        family = seq(0x1F468, ranges.ZERO_WIDTH_JOINER, 0x1F469)

        def chunks():
            # Simulates a file read in pieces smaller than one sequence.
            for piece in (family[:2], family[2:]):
                for ch in piece:
                    yield ch

        self.assertEqual(list(iter_sequences(chunks())), [family])


if __name__ == "__main__":
    unittest.main()
