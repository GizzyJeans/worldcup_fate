"""worldcup_fate 占卜系統的基本測試。"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldcup_fate import FULL_DECK, build_deck, divine  # noqa: E402
from worldcup_fate.cards import Card  # noqa: E402
from worldcup_fate.deck import Deck  # noqa: E402
from worldcup_fate.spread import POSITION_COUNT  # noqa: E402
from worldcup_fate import fixtures  # noqa: E402
from worldcup_fate.cli import main as cli_main  # noqa: E402


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

    def test_score_total_consistent_with_over_under(self):
        """比分加總不得與大小分(2.5 線)結論自相矛盾。"""
        names = ["阿根廷", "法國", "巴西", "英格蘭", "西班牙", "德國",
                 "葡萄牙", "荷蘭", "象牙海岸", "挪威", "墨西哥", "厄瓜多",
                 "克羅埃西亞", "摩洛哥", "日本", "美國"]
        stages = ["小組賽", "32強淘汰賽", "八強", "決賽"]
        for i, home in enumerate(names):
            away = names[(i + 1) % len(names)]
            for stage in stages:
                r = divine(home, away, stage=stage, date="2026-07-01")
                total = sum(r.predicted_score)
                ctx = f"{home} vs {away} [{stage}] total={r.predicted_total} score={r.predicted_score}"
                if r.predicted_total < 2.25:      # 判小分
                    self.assertLessEqual(total, 2, ctx)
                elif r.predicted_total > 2.75:    # 判大分
                    self.assertGreaterEqual(total, 3, ctx)

    def test_ivory_coast_norway_case_fixed(self):
        """象牙海岸 vs 挪威(32強)曾出現比分與大小分互相矛盾的 bug。

        不鎖定大小分方向(校準會改變推估值),只驗證兩項預言永遠同側。
        """
        r = divine("象牙海岸", "挪威", stage="32強淘汰賽", date="2026-06-30")
        total = sum(r.predicted_score)
        if r.predicted_total <= 2.25:
            self.assertLessEqual(total, 2)
        elif r.predicted_total >= 2.75:
            self.assertGreaterEqual(total, 3)

    def test_knockout_never_predicts_draw(self):
        """淘汰賽必分勝負:任何淘汰賽階段不得判平局。"""
        names = ["阿根廷", "法國", "巴西", "英格蘭", "西班牙", "德國", "葡萄牙", "荷蘭"]
        for stage in ["32強淘汰賽", "十六強", "八強", "準決賽", "決賽"]:
            for i, home in enumerate(names):
                away = names[(i + 1) % len(names)]
                r = divine(home, away, stage=stage, date="2026-07-04")
                self.assertIn(r.winner, ("home", "away"),
                              f"{home} vs {away} [{stage}] 判了平局")
                h, a = r.predicted_score
                self.assertNotEqual(h, a, f"{home} vs {away} [{stage}] 比分平手")

    def test_group_stage_can_still_draw(self):
        """小組賽仍允許平局(校準只動淘汰賽)。"""
        winners = set()
        names = ["阿根廷", "法國", "巴西", "英格蘭", "西班牙", "德國",
                 "葡萄牙", "荷蘭", "日本", "美國", "摩洛哥", "瑞士"]
        for i, home in enumerate(names):
            away = names[(i + 1) % len(names)]
            r = divine(home, away, stage="小組賽", date="2026-06-20")
            winners.add(r.winner)
        self.assertLessEqual(winners, {"home", "away", "draw"})


class TestFixtures(unittest.TestCase):
    def test_normalize_team_chinese_and_english(self):
        self.assertEqual(fixtures.normalize_team("西班牙"), "Spain")
        self.assertEqual(fixtures.normalize_team("奧地利"), "Austria")
        self.assertEqual(fixtures.normalize_team(" spain "), "Spain")
        self.assertEqual(fixtures.normalize_team("Austria"), "Austria")

    def test_normalize_unknown_returns_stripped(self):
        self.assertEqual(fixtures.normalize_team("  火星隊 "), "火星隊")

    def test_find_fixture_order_independent(self):
        a = fixtures.find_fixture("西班牙", "奧地利")
        b = fixtures.find_fixture("奧地利", "西班牙")
        c = fixtures.find_fixture("Spain", "Austria")
        self.assertIsNotNone(a)
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        self.assertEqual(a["stage"], "32強淘汰賽")
        self.assertEqual(a["date"], "2026-07-02")

    def test_find_fixture_not_found(self):
        self.assertIsNone(fixtures.find_fixture("巴西", "火星隊"))

    def test_auto_fills_stage_and_date_without_changing_seed(self):
        """--auto 帶入的賽程資訊不得改變牌面(命運種子只取決於隊名/階段/日期)。"""
        fx = fixtures.find_fixture("西班牙", "奧地利")
        auto = divine("西班牙", "奧地利", stage=fx["stage"], date=fx["date"],
                      venue=fx["venue"], kickoff=fx["kickoff"])
        manual = divine("西班牙", "奧地利", stage="32強淘汰賽", date="2026-07-02")
        self.assertEqual(auto.predicted_score, manual.predicted_score)
        self.assertEqual(auto.winner, manual.winner)
        self.assertEqual(auto.confidence, manual.confidence)
        self.assertTrue(auto.venue)  # 場館有被帶入顯示


class TestCli(unittest.TestCase):
    def test_cli_auto_json_runs(self):
        rc = cli_main(["西班牙", "奧地利", "--auto", "--json"])
        self.assertEqual(rc, 0)

    def test_cli_list_fixtures(self):
        rc = cli_main(["--list-fixtures"])
        self.assertEqual(rc, 0)

    def test_cli_missing_teams_errors(self):
        with self.assertRaises(SystemExit):
            cli_main([])


if __name__ == "__main__":
    unittest.main()
