"""校準回測:以 2026 世界杯 32 強九場實際賽果驗證解讀引擎。

校準紀錄:
- 2026-07-03 第一輪(六場):進球能量除數 14.0 -> 9.0;淘汰賽不判平局。
  校準前:勝負 3/6、大小分方向 2/6、總球數平均絕對誤差 0.97。
- 2026-07-04 第二輪(擴充至九場):讓分盤依優勢等級收淺;新增高動盪大牌
  之延長/PK 風險示警(澳埃 PK 之戰實證,九場回測無誤報)。

賽果來源:FIFA / ESPN 賽果頁。進球數以 90 分鐘常規時間計(讓分/大小分
慣例),晉級方另欄記錄(延長/PK 之結果)。測試鎖定校準後的最低準確度,
防止日後改動造成退步。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldcup_fate import divine  # noqa: E402

# (主隊, 客隊, 階段, 日期, 常規主進球, 常規客進球, 晉級方 "home"/"away")
ACTUAL_RESULTS = [
    ("象牙海岸", "挪威", "32強淘汰賽", "2026-06-30", 1, 2, "away"),
    ("法國", "瑞典", "32強淘汰賽", "2026-06-30", 3, 0, "home"),
    ("墨西哥", "厄瓜多", "32強淘汰賽", "2026-07-01", 2, 0, "home"),
    ("西班牙", "奧地利", "32強淘汰賽", "2026-07-02", 3, 0, "home"),
    ("葡萄牙", "克羅埃西亞", "32強淘汰賽", "2026-07-02", 2, 1, "home"),
    ("瑞士", "阿爾及利亞", "32強淘汰賽", "2026-07-02", 2, 0, "home"),
    # 第二輪新增:澳埃 1:1 後 PK 埃及晉級;阿維 1:1 後延長 3:2
    ("澳洲", "埃及", "32強淘汰賽", "2026-07-03", 1, 1, "away"),
    ("阿根廷", "維德角", "32強淘汰賽", "2026-07-03", 1, 1, "home"),
    ("哥倫比亞", "迦納", "32強淘汰賽", "2026-07-03", 1, 0, "home"),
]


def _readings():
    for home, away, stage, date, hg, ag, advancer in ACTUAL_RESULTS:
        yield divine(home, away, stage=stage, date=date), hg, ag, advancer


class TestCalibration(unittest.TestCase):
    def test_no_draw_in_knockout_dataset(self):
        for r, _, _, _ in _readings():
            self.assertIn(r.winner, ("home", "away"))

    def test_advancer_accuracy(self):
        hits = sum(1 for r, _, _, adv in _readings() if r.winner == adv)
        self.assertGreaterEqual(hits, 6, f"晉級方命中僅 {hits}/9,低於校準水準 6/9")

    def test_over_under_accuracy(self):
        hits = 0
        for r, hg, ag, _ in _readings():
            predicted_over = r.predicted_total > 2.5
            actual_over = (hg + ag) > 2.5
            if predicted_over == actual_over:
                hits += 1
        self.assertGreaterEqual(hits, 6, f"大小分方向僅 {hits}/9,低於校準水準 6/9")

    def test_total_goals_mean_error(self):
        errors = [abs(r.predicted_total - (hg + ag)) for r, hg, ag, _ in _readings()]
        mean_error = sum(errors) / len(errors)
        self.assertLessEqual(
            mean_error, 0.6,
            f"總球數平均絕對誤差 {mean_error:.2f},高於校準水準 0.6",
        )

    def test_handicap_line_shallow_unless_dominant(self):
        """些微優勢(戰力差 <=5)之局,建議盤口不得深於 0.5。"""
        for r, _, _, _ in _readings():
            if r.knife_edge:
                self.assertLessEqual(r.handicap_line, 0.5)
            self.assertLessEqual(r.handicap_line, 1.5,
                                 "回測資料集內無壓倒性之局,盤口不應深於 1.5")

    def test_overtime_signal_no_false_alarm_beyond_knife_edge(self):
        """高動盪大牌示警(非一線之間者)於九場回測中僅澳埃一例,且該場
        確實戰至 PK——此測試鎖定訊號的無誤報紀錄。"""
        flagged = [
            (r.home, r.away)
            for r, _, _, _ in _readings()
            if r.overtime_risk and not r.knife_edge
        ]
        self.assertEqual(flagged, [("澳洲", "埃及")])


if __name__ == "__main__":
    unittest.main()
