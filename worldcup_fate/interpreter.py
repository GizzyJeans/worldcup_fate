"""解讀引擎:把抽出的牌轉化為客觀的比賽預言。

所有預言皆由牌面數值依固定規則推導,完全不參考球隊主觀強弱、賭盤賠率
或過盤率。占卜師只忠實於命運攤開的牌。
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

from .cards import CardEnergy
from .deck import Deck, DrawnCard
from .spread import WORLD_CUP_SPREAD, POSITION_COUNT


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# 淘汰賽階段的判別關鍵字:32強/十六強/八強(含「強」)、淘汰、決賽/準決賽
_KNOCKOUT_MARKERS = ("強", "淘汰", "決賽")


def _is_knockout(stage: str) -> bool:
    """淘汰賽必分勝負(延長/PK),不存在平局收場。"""
    return any(marker in stage for marker in _KNOCKOUT_MARKERS)


@dataclass
class MatchReading:
    """一場對戰的完整占卜結果。"""

    home: str
    away: str
    stage: str
    date: str
    cards: dict[str, DrawnCard]          # position key -> DrawnCard

    # 選填的賽事資訊(僅供顯示,不影響命運種子)
    venue: str = ""
    kickoff: str = ""
    source: str = ""

    # 推導出的數值結果(便於程式化取用)
    winner: str = ""                      # "home" / "away" / "draw"
    knife_edge: bool = False              # 淘汰賽中戰力差極小、一線之間的對決
    win_text: str = ""
    handicap_text: str = ""
    totals_text: str = ""
    halves_text: str = ""
    predicted_score: tuple[int, int] = (0, 0)
    predicted_total: float = 0.0
    confidence: int = 0

    # 內部能量快取
    _energy: dict[str, CardEnergy] = field(default_factory=dict, repr=False)

    # ---- 取能量小工具 ---------------------------------------------------- #
    def _e(self, key: str) -> CardEnergy:
        if key not in self._energy:
            dc = self.cards[key]
            self._energy[key] = dc.card.effective(dc.reversed)
        return self._energy[key]

    # ---- 主推導流程 ------------------------------------------------------ #
    def compute(self) -> "MatchReading":
        home_e = self._e("home")
        away_e = self._e("away")
        fh_e = self._e("first_half")
        sh_e = self._e("second_half")
        tot_e = self._e("total_goals")
        wild_e = self._e("wildcard")
        verdict_e = self._e("verdict")

        # ---- 戰力綜合 ---------------------------------------------------- #
        power_home = home_e.attack + home_e.defense + home_e.momentum + home_e.goal * 0.2
        power_away = away_e.attack + away_e.defense + away_e.momentum + away_e.goal * 0.2
        margin = power_home - power_away

        # 變數削弱信心、模糊戰力差距
        chaos = (wild_e.volatility + tot_e.volatility * 0.5 + verdict_e.volatility * 0.5)

        # ---- 勝負判定 ---------------------------------------------------- #
        # 校準(2026-07-03,依 32 強六場實績):淘汰賽必分勝負,戰力差
        # 落在 ±2 之內不再判平局,改判「一線之間」並以差距方向定晉級方。
        knockout = _is_knockout(self.stage)
        if margin > 2.0:
            self.winner = "home"
            favored, underdog = self.home, self.away
        elif margin < -2.0:
            self.winner = "away"
            favored, underdog = self.away, self.home
        elif knockout:
            self.knife_edge = True
            self.winner = "home" if margin >= 0 else "away"
            if self.winner == "home":
                favored, underdog = self.home, self.away
            else:
                favored, underdog = self.away, self.home
        else:
            self.winner = "draw"
            favored = underdog = ""

        if self.winner == "draw":
            self.win_text = (
                f"牌面天秤持平(戰力差 {margin:+.1f}),雙方旗鼓相當,"
                f"平局氣息濃厚;若分勝負,將是極小差距的拉鋸。"
            )
        elif self.knife_edge:
            self.win_text = (
                f"牌面一線之間(戰力差 {margin:+.1f}),**{favored}** 僅具毫釐之先;"
                f"90 分鐘恐難分高下,不排除延長甚至 PK,{underdog} 隨時可能翻越。"
            )
        else:
            edge = abs(margin)
            tier = "壓倒性" if edge > 8 else "明顯" if edge > 5 else "些微"
            self.win_text = (
                f"牌面傾向 **{favored}** 勝出(戰力差 {margin:+.1f}),"
                f"優勢屬「{tier}」等級;{underdog} 須仰賴關鍵變數方能翻盤。"
            )

        # ---- 大小分 ------------------------------------------------------ #
        goal_energy = (
            home_e.goal + away_e.goal
            + fh_e.goal + sh_e.goal
            + tot_e.goal * 1.5
            + (home_e.attack + away_e.attack) * 0.3
            - (home_e.defense + away_e.defense) * 0.2
        )
        # 校準(2026-07-03):原除數 14.0 有系統性小分偏誤——32 強六場推估
        # 均值 1.70 球、實際均值 2.67 球;改為 9.0 後平均絕對誤差 0.97 → 0.34。
        predicted_total = _clamp(goal_energy / 9.0, 0.4, 5.2)
        self.predicted_total = round(predicted_total, 2)

        line = 2.5
        if predicted_total >= line + 0.25:
            lean = f"**大分 (Over {line})**"
        elif predicted_total <= line - 0.25:
            lean = f"**小分 (Under {line})**"
        else:
            lean = f"貼近 {line} 的分界,傾向不明、屬危險盤"
        self.totals_text = (
            f"進球潮強度推估全場約 **{self.predicted_total} 球**,標準盤 {line} 之下,牌面傾向 {lean}。"
        )

        # ---- 比分推估 ---------------------------------------------------- #
        # 比分加總必須與大小分推估同調,否則會出現「比分 1:2(共 3 球)卻判小分」
        # 的自相矛盾。因此調整勝負時採「在兩隊之間挪移進球」而非「額外加球」,
        # 平手比分也與 2.5 線同側,確保兩項預言一致。
        total_goals_int = int(round(predicted_total))
        if power_home + power_away <= 0:
            home_share = 0.5
        else:
            home_share = power_home / (power_home + power_away)

        if total_goals_int <= 0:
            # 幾無進球卻有勝負傾向時,給出最小勝局
            if self.winner == "home":
                home_goals, away_goals = 1, 0
            elif self.winner == "away":
                home_goals, away_goals = 0, 1
            else:
                home_goals, away_goals = 0, 0
        elif self.winner == "draw":
            # 平局比分加總須為偶數,並與大小分傾向落在 2.5 的同一側
            if predicted_total > line:
                home_goals = away_goals = 2
            else:
                home_goals = away_goals = 1 if total_goals_int >= 2 else 0
        elif self.knife_edge:
            # 一線之間:給最小差距的決勝比分,總球數與大小分傾向同側
            win_g, lose_g = (2, 1) if predicted_total >= line else (1, 0)
            if self.winner == "home":
                home_goals, away_goals = win_g, lose_g
            else:
                home_goals, away_goals = lose_g, win_g
        else:
            home_goals = max(0, min(total_goals_int,
                                    int(round(total_goals_int * home_share))))
            away_goals = total_goals_int - home_goals
            # 維持總進球不變,把進球在兩隊間挪移以符合勝負結論
            if self.winner == "home" and home_goals <= away_goals:
                move = (away_goals - home_goals) // 2 + 1
                home_goals += move
                away_goals -= move
            elif self.winner == "away" and away_goals <= home_goals:
                move = (home_goals - away_goals) // 2 + 1
                away_goals += move
                home_goals -= move

        self.predicted_score = (home_goals, away_goals)

        # ---- 讓分/受讓 --------------------------------------------------- #
        diff = abs(home_goals - away_goals)
        if self.winner == "draw" or diff == 0:
            self.handicap_text = (
                "牌面無明顯讓步空間,**平手盤 (0)** 最為貼合;受讓方價值浮現。"
            )
        elif self.knife_edge:
            favored_name = self.home if self.winner == "home" else self.away
            underdog_name = self.away if self.winner == "home" else self.home
            self.handicap_text = (
                f"一線之盤:**{favored_name}** 至多讓 **0.5 球**;"
                f"平手盤與受讓 {underdog_name} 皆具價值,深盤不宜。"
            )
        else:
            # 讓分線取在預期分差附近的半球盤
            line_h = diff - 0.5
            if self.winner == "home":
                self.handicap_text = (
                    f"主隊 **{self.home}** 可讓 **{line_h:.1f} 球**;"
                    f"若盤口讓得更深,受讓 {self.away} 反有保護價值。"
                )
            else:
                self.handicap_text = (
                    f"客隊 **{self.away}** 可讓 **{line_h:.1f} 球**;"
                    f"若盤口讓得更深,受讓 {self.home} 反有保護價值。"
                )

        # ---- 上下半場 ---------------------------------------------------- #
        fh_score = fh_e.goal + fh_e.momentum + fh_e.attack * 0.3
        sh_score = sh_e.goal + sh_e.momentum + sh_e.attack * 0.3
        if fh_score - sh_score > 1.5:
            hotter = "上半場"
            half_lead = "開賽火力旺盛,前 45 分鐘即見高潮"
        elif sh_score - fh_score > 1.5:
            hotter = "下半場"
            half_lead = "上半場按兵不動,易邊後體能與調度才見分曉"
        else:
            hotter = "兩個半場"
            half_lead = "全場節奏平均,進球可能散落於任何時段"

        mom_shift = sh_e.momentum - fh_e.momentum
        if mom_shift > 1.5:
            shift_text = "氣勢呈「漸入佳境」之勢,下半場明顯升溫"
        elif mom_shift < -1.5:
            shift_text = "氣勢呈「虎頭蛇尾」之勢,下半場逐漸轉冷"
        else:
            shift_text = "上下半場氣勢延續一致,無明顯轉折"
        self.halves_text = (
            f"進球時段集中於 **{hotter}**({half_lead});{shift_text}。"
        )

        # ---- 信心度 ------------------------------------------------------ #
        base = 72.0
        base -= chaos * 1.6                       # 變數越高,信心越低
        if self.winner != "draw":
            base += min(abs(margin), 10) * 1.2    # 戰力差越大越有信心
        else:
            base -= 6                             # 平局本就難測
        if self.knife_edge:
            base -= 6                             # 一線之間,與平局同樣難測
        base += verdict_e.momentum                # 定論之牌的氣勢加成
        self.confidence = int(_clamp(round(base), 30, 94))

        return self


def divine(home: str, away: str, stage: str = "小組賽", date: str | None = None,
           venue: str = "", kickoff: str = "", source: str = "") -> MatchReading:
    """為一場對戰進行占卜,回傳已完成推導的 MatchReading。

    venue / kickoff / source 僅供顯示,不參與命運種子的計算,因此帶入賽事
    資訊不會改變牌面。
    """
    if date is None:
        date = _dt.date.today().isoformat()

    deck = Deck.for_match(home, away, stage, date)
    drawn = deck.draw(POSITION_COUNT)
    cards = {pos.key: dc for pos, dc in zip(WORLD_CUP_SPREAD, drawn)}

    reading = MatchReading(
        home=home, away=away, stage=stage, date=date, cards=cards,
        venue=venue, kickoff=kickoff, source=source,
    )
    return reading.compute()
