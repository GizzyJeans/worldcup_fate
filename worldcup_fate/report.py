"""把 MatchReading 渲染成占卜師口吻的繁體中文報告。"""

from __future__ import annotations

from .interpreter import MatchReading
from .spread import WORLD_CUP_SPREAD


def _bar(value: float, lo: float, hi: float, width: int = 10) -> str:
    """把數值畫成簡單的長條。"""
    span = hi - lo
    filled = 0 if span == 0 else int(round((value - lo) / span * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "·" * (width - filled)


def render(reading: MatchReading) -> str:
    r = reading
    lines: list[str] = []
    add = lines.append

    add("=" * 60)
    add("　　🔮  2026 世界杯 · 塔羅戰局占卜  🔮")
    add("=" * 60)
    add(f"對戰　：{r.home}（主）　VS　{r.away}（客）")
    add(f"階段　：{r.stage}")
    add(f"日期　：{r.date}")
    if r.venue:
        add(f"場館　：{r.venue}")
    if r.kickoff:
        add(f"開賽　：{r.kickoff}")
    add(f"牌陣　：世界杯七張牌戰局牌陣")
    add("")

    # ---- 牌陣明細 -------------------------------------------------------- #
    add("──【 攤開的命運之牌 】" + "─" * 36)
    for pos in WORLD_CUP_SPREAD:
        dc = r.cards[pos.key]
        c = dc.card
        tag = "大牌" if c.arcana == "major" else "小牌"
        add(f"◆ {pos.name}：{c.name}（{c.en_name}）— {dc.orientation} [{tag}]")
        add(f"    {dc.meaning}")
    add("")

    # ---- 預言 ------------------------------------------------------------ #
    add("──【 占卜師的預言 】" + "─" * 38)
    add(f"【勝　負】{r.win_text}")
    add(f"【讓受讓】{r.handicap_text}")
    add(f"【大小分】{r.totals_text}")
    add(f"【上下半】{r.halves_text}")
    add("")
    add(f"  ⚑ 預期比分：{r.home} {r.predicted_score[0]} : {r.predicted_score[1]} {r.away}")
    add(f"  ⚑ 預期總進球：約 {r.predicted_total} 球")
    add(f"  ⚑ 占卜信心度：{r.confidence}%  [{_bar(r.confidence, 0, 100)}]")
    add("")

    add("─" * 60)
    add("※ 本占卜純依牌面客觀推導,不參考賭盤賠率、過盤率或主觀強弱。")
    add("※ 命運已定,同場同日不可重抽。牌面僅供參酌,勝負終須綠茵見真章。")
    if r.source:
        add(f"※ 賽程資料來源:{r.source}(以 FIFA 官方為準)")
    add("=" * 60)

    return "\n".join(lines)
