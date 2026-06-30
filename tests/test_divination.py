"""worldcup_fate 占卜系統的基本測試。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldcup_fate import FULL_DECK, build_deck, divine  # noqa: E402
from worldcup_fate.cards import Card  # noqa: E402
from worldcup_fate.deck import Deck  # noqa: E402
from worldcup_fate.spread import POSITION_COUNT  # noqa: E402


class TestDeck(unittest.TestCase):
    def test_full_deck_is_78_cards(self):
        self.assertEqual(len(FULL_DECK), 78)

    def test_deck_has_22_major_and_56_minor(self):
        majors = [c for c in FULL_DECK if c.arcana == "major"]
        minors = [c for c in FULL_DECK if c.arcana == "minor"]
        self.assertEqual(len(majors), 22)
        self.assertEqual(len(minors), 56)

    def test_no_duplicate_card_names(self):
        names = [c.name for c in FULL_DECK]
        self.assertEqual(len(names), len(set(names)))

    def test_attributes_within_bounds(self):
        for c in FULL_DECK:
            for attr in ("attack", "defense", "volatility", "goal"):
                value = getattr(c, attr)
                self.assertGreaterEqual(value, 0, f"{c.name}.{attr}")
                self.assertLessEqual(value, 10, f"{c.name}.{attr}")
            self.assertGreaterEqual(c.momentum, -5)
            self.assertLessEqual(c.momentum, 5)

    def test_reversed_energy_increases_volatility(self):
        for c in FULL_DECK:
            up = c.effective(False)
            rev = c.effective(True)
            self.assertGreaterEqual(rev.volatility, up.volatility)


class TestDraw(unittest.TestCase):
    def test_draw_count(self):
        deck = Deck(seed=1)
        drawn = deck.draw(POSITION_COUNT)
        self.assertEqual(len(drawn), POSITION_COUNT)

    def test_drawn_cards_are_unique(self):
        deck = Deck(seed=42)
        drawn = deck.draw(POSITION_COUNT)
        names = [d.card.name for d in drawn]
        self.assertEqual(len(names), len(set(names)))

    def test_same_seed_same_draw(self):
        a = Deck(seed=99).draw(POSITION_COUNT)
        b = Deck(seed=99).draw(POSITION_COUNT)
        self.assertEqual(
            [(d.card.name, d.reversed) for d in a],
            [(d.card.name, d.reversed) for d in b],
        )

    def test_draw_too_many_raises(self):
        with self.assertRaises(ValueError):
            Deck(seed=1).draw(100)


class TestDivination(unittest.TestCase):
    def test_fate_is_deterministic(self):
        r1 = divine("阿根廷", "法國", stage="決賽", date="2026-07-19")
        r2 = divine("阿根廷", "法國", stage="決賽", date="2026-07-19")
        self.assertEqual(r1.predicted_score, r2.predicted_score)
        self.assertEqual(r1.winner, r2.winner)
        self.assertEqual(r1.confidence, r2.confidence)

    def test_different_match_can_differ(self):
        r1 = divine("阿根廷", "法國", date="2026-07-19")
        r2 = divine("巴西", "英格蘭", date="2026-07-19")
        # 至少抽到的牌序不應完全相同
        c1 = [d.card.name for d in r1.cards.values()]
        c2 = [d.card.name for d in r2.cards.values()]
        self.assertNotEqual(c1, c2)

    def test_all_dimensions_present(self):
        r = divine("西班牙", "德國", stage="八強")
        self.assertTrue(r.win_text)
        self.assertTrue(r.handicap_text)
        self.assertTrue(r.totals_text)
        self.assertTrue(r.halves_text)

    def test_winner_is_valid(self):
        r = divine("葡萄牙", "荷蘭")
        self.assertIn(r.winner, ("home", "away", "draw"))

    def test_confidence_in_range(self):
        r = divine("克羅埃西亞", "摩洛哥")
        self.assertGreaterEqual(r.confidence, 30)
        self.assertLessEqual(r.confidence, 94)

    def test_score_consistent_with_winner(self):
        for home, away in [("A", "B"), ("巴西", "日本"), ("X", "Y"), ("甲", "乙")]:
            r = divine(home, away)
            h, a = r.predicted_score
            if r.winner == "home":
                self.assertGreater(h, a, f"{home} vs {away}")
            elif r.winner == "away":
                self.assertGreater(a, h, f"{home} vs {away}")
            else:
                self.assertEqual(h, a, f"{home} vs {away}")


if __name__ == "__main__":
    unittest.main()
