"""校準回測:以 2026 世界杯 32 強六場實際賽果驗證解讀引擎。

這六場是 2026-07-03 校準時使用的實績資料(來源:FIFA / ESPN 賽果頁)。
測試鎖定校準後的最低準確度,防止日後改動讓引擎退步到校準前的水準
(校準前:勝負 3/6、大小分方向 2/6、總球數平均絕對誤差 0.97)。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldcup_fate import divine  # noqa: E402

# (主隊, 客隊, 階段, 日期, 主隊實際進球, 客隊實際進球)
ACTUAL_RESULTS = [
    ("象牙海岸", "挪威", "32強淘汰賽", "2026-06-30", 1, 2),
    ("法國", "瑞典", "32強淘汰賽", "2026-06-30", 3, 0),
    ("墨西哥", "厄瓜多", "32強淘汰賽", "2026-07-01", 2, 0),
    ("西班牙", "奧地利", "32強淘汰賽", "2026-07-02", 3, 0),
    ("葡萄牙", "克羅埃西亞", "32強淘汰賽", "2026-07-02", 2, 1),
    ("瑞士", "阿爾及利亞", "32強淘汰賽", "2026-07-02", 2, 0),
]


def _readings():
    for home, away, stage, date, hg, ag in ACTUAL_RESULTS:
        yield divine(home, away, stage=stage, date=date), hg, ag


class TestCalibration(unittest.TestCase):
    def test_no_draw_in_knockout_dataset(self):
        for r, _, _ in _readings():
            self.assertIn(r.winner, ("home", "away"))

    def test_winner_accuracy(self):
        hits = 0
        for r, hg, ag in _readings():
            actual = "home" if hg > ag else "away" if ag > hg else "draw"
            if r.winner == actual:
                hits += 1
        self.assertGreaterEqual(hits, 4, f"勝負命中僅 {hits}/6,低於校準水準 4/6")

    def test_over_under_accuracy(self):
        hits = 0
        for r, hg, ag in _readings():
            predicted_over = r.predicted_total > 2.5
            actual_over = (hg + ag) > 2.5
            if predicted_over == actual_over:
                hits += 1
        self.assertGreaterEqual(hits, 4, f"大小分方向僅 {hits}/6,低於校準水準 4/6")

    def test_total_goals_mean_error(self):
        errors = [abs(r.predicted_total - (hg + ag)) for r, hg, ag in _readings()]
        mean_error = sum(errors) / len(errors)
        self.assertLessEqual(
            mean_error, 0.6,
            f"總球數平均絕對誤差 {mean_error:.2f},高於校準水準 0.6",
        )


if __name__ == "__main__":
    unittest.main()
