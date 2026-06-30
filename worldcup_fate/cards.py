"""塔羅牌資料模型與完整 78 張牌組。

每張牌除了傳統牌義外,另外帶有一組「足球解讀屬性」,這些屬性是占卜
引擎用來客觀推導比賽走勢的依據:

    attack   : 攻擊能量 (0-10) —— 火力、壓迫、製造機會的傾向
    defense  : 防守能量 (0-10) —— 穩固、紀律、抵抗壓力的傾向
    momentum : 氣勢 (-5..+5)   —— 正值代表上升、負值代表衰退
    volatility: 變數 (0-10)    —— 混亂、爆冷、紅黃牌、突發事件的傾向
    goal     : 進球傾向 (0-10) —— 牌面指向「會有進球」的強度

大阿爾克那為手工逐張定義;小阿爾克那則由「花色基礎屬性 + 階級調整」
系統化推導,確保整副牌的數值口徑一致、客觀。
"""

from __future__ import annotations

from dataclasses import dataclass


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Card:
    """一張塔羅牌。"""

    name: str          # 中文牌名
    en_name: str       # 英文牌名
    arcana: str        # "major" 或 "minor"
    suit: str | None   # 小阿爾克那花色,大牌為 None
    rank: str | None   # 小阿爾克那階級,大牌為 None
    upright: str       # 正位牌義(足球視角)
    reversed: str      # 逆位牌義(足球視角)
    attack: float
    defense: float
    momentum: float
    volatility: float
    goal: float

    def effective(self, is_reversed: bool) -> "CardEnergy":
        """回傳考量正逆位後的有效能量。

        逆位代表能量受阻或反轉:攻擊與進球傾向被削弱,氣勢被抽離甚至倒轉,
        而場面的不確定性(變數)反而升高。
        """
        if not is_reversed:
            return CardEnergy(
                attack=self.attack,
                defense=self.defense,
                momentum=self.momentum,
                volatility=self.volatility,
                goal=self.goal,
            )
        return CardEnergy(
            attack=_clamp(self.attack * 0.6, 0, 10),
            defense=_clamp(self.defense * 0.7, 0, 10),
            momentum=_clamp(-self.momentum * 0.5, -5, 5),
            volatility=_clamp(self.volatility + 2, 0, 10),
            goal=_clamp(self.goal * 0.7, 0, 10),
        )


@dataclass(frozen=True)
class CardEnergy:
    """一張牌在特定正逆位下,實際投入解讀的能量值。"""

    attack: float
    defense: float
    momentum: float
    volatility: float
    goal: float


# --------------------------------------------------------------------------- #
# 大阿爾克那 (22 張)
# 欄位: (名稱, 英文, 正位, 逆位, attack, defense, momentum, volatility, goal)
# --------------------------------------------------------------------------- #
_MAJOR: list[tuple] = [
    ("愚者", "The Fool",
     "無懼的冒進,初生之犢、勇於壓上,但戰術紀律鬆散、後防易露空檔。",
     "魯莽招致失誤,過度冒險反成隱患,陣腳易亂。",
     6, 3, 3, 9, 6),
    ("魔術師", "The Magician",
     "技術全面、調度自如,核心球員能無中生有地創造機會。",
     "華而不實,空有控球卻轉化不成得分。",
     8, 5, 4, 4, 7),
    ("女祭司", "The High Priestess",
     "沉著耐心、後發制人,以靜制動的防守智慧。",
     "過度保守、隱忍失機,被動挨打。",
     3, 8, 0, 3, 3),
    ("皇后", "The Empress",
     "豐沛的進攻產出,中前場源源不絕地餵球。",
     "進攻效率下滑,空有場面卻收成不佳。",
     7, 6, 2, 3, 7),
    ("皇帝", "The Emperor",
     "鐵血紀律、結構嚴明,以強大的中後場掌控全局。",
     "過於僵化,體系受制、應變不足。",
     6, 9, 1, 2, 4),
    ("教皇", "The Hierophant",
     "傳統穩健、按部就班,紀律與經驗主導比賽。",
     "墨守成規、缺乏變化,被對手摸透。",
     5, 7, 0, 2, 4),
    ("戀人", "The Lovers",
     "團隊默契極佳、配合流暢,前後場連動順暢。",
     "抉擇猶豫、默契出現裂痕,關鍵時刻失衡。",
     6, 6, 2, 5, 6),
    ("戰車", "The Chariot",
     "氣勢如虹、強勢推進,以衝勁碾壓對手奪取主動。",
     "橫衝直撞失去方向,衝太快反留後患。",
     9, 6, 5, 4, 7),
    ("力量", "Strength",
     "剛柔並濟、掌控節奏,在對抗中展現韌性與耐力。",
     "氣力放盡後力有未逮,韌性鬆動。",
     7, 8, 3, 3, 6),
    ("隱者", "The Hermit",
     "謹慎收斂、低調務實,刻意放慢節奏尋求穩定。",
     "過度退縮、孤立保守,進攻熄火。",
     3, 7, -2, 3, 2),
    ("命運之輪", "Wheel of Fortune",
     "局勢翻轉的轉捩點,氣勢與運勢急速流動。",
     "時運不濟,情勢朝不利方向滑落。",
     6, 5, 3, 9, 6),
    ("正義", "Justice",
     "勢均力敵、天秤持平,雙方旗鼓相當難分高下。",
     "判罰爭議、失衡,公平天秤遭打破。",
     5, 5, 0, 3, 4),
    ("吊人", "The Hanged Man",
     "僵持膠著、自我犧牲,場面陷入停滯與消耗。",
     "犧牲無回報、停滯惡化,陷入泥沼。",
     3, 6, -3, 4, 2),
    ("死神", "Death",
     "格局劇變、新舊交替,一次決定性的轉折扭轉戰局。",
     "轉變受阻、舊勢力反撲,變革難產。",
     5, 4, -1, 8, 5),
    ("節制", "Temperance",
     "節奏調和、攻守平衡,耐心經營、穩中求進。",
     "失去平衡、調度失準,節奏被打亂。",
     5, 6, 1, 2, 4),
    ("惡魔", "The Devil",
     "高強度肉搏、犯規不斷,黑暗而粗野的對抗。",
     "掙脫束縛,但情緒失控招致更多衝突。",
     7, 6, 1, 8, 5),
    ("高塔", "The Tower",
     "突如其來的崩塌,紅牌、烏龍或瞬間瓦解,場面劇烈動盪。",
     "崩潰雖至但餘波稍緩,仍難逃震盪。",
     8, 2, -4, 10, 8),
    ("星星", "The Star",
     "希望與流暢並存,順勢而為、發揮自如。",
     "信心不足、發揮失常,期望落空。",
     6, 6, 2, 3, 6),
    ("月亮", "The Moon",
     "迷霧重重、虛實難辨,場面混沌、暗藏陷阱。",
     "迷霧漸散但疑雲未消,仍易誤判。",
     4, 5, -2, 8, 4),
    ("太陽", "The Sun",
     "光芒萬丈、全面壓制,活力充沛地走向勝利。",
     "光彩略減,優勢仍在但未盡全功。",
     9, 7, 5, 2, 8),
    ("審判", "Judgement",
     "決定性的覺醒與爆發,關鍵時刻一錘定音。",
     "猶豫錯失審判時機,翻盤未果。",
     7, 6, 4, 5, 7),
    ("世界", "The World",
     "圓滿完整、爐火純青,全面而成熟地掌控比賽。",
     "功虧一簣、收尾不順,圓滿生變。",
     8, 8, 3, 2, 6),
]


# --------------------------------------------------------------------------- #
# 小阿爾克那 (56 張) —— 系統化生成
# --------------------------------------------------------------------------- #
# 花色基礎屬性與主題
_SUITS: dict[str, dict] = {
    "權杖": {
        "en": "Wands",
        "theme": "進攻火力與衝勁",
        "reading": "場面偏向主動壓迫、火力外放",
        "base": dict(attack=7, defense=4, momentum=2, volatility=6, goal=7),
    },
    "聖杯": {
        "en": "Cups",
        "theme": "流暢控球與團隊默契",
        "reading": "場面偏向控球串連、以默契調度節奏",
        "base": dict(attack=5, defense=6, momentum=1, volatility=4, goal=5),
    },
    "寶劍": {
        "en": "Swords",
        "theme": "對抗糾纏與犯規衝突",
        "reading": "場面偏向激烈對抗、犯規與爭議不斷",
        "base": dict(attack=6, defense=5, momentum=0, volatility=8, goal=4),
    },
    "錢幣": {
        "en": "Pentacles",
        "theme": "穩固防守與體能耐力",
        "reading": "場面偏向穩紮穩打、重防守與耐力",
        "base": dict(attack=4, defense=8, momentum=0, volatility=3, goal=3),
    },
}

# 階級主題與屬性調整 (delta)
_RANKS: list[tuple] = [
    # (中文, 英文, 主題, d_attack, d_def, d_mom, d_vol, d_goal)
    ("王牌", "Ace", "純粹的能量與嶄新開端", 1, 0, 2, 0, 1),
    ("二", "Two", "抉擇與平衡", 0, 0, 0, 0, 0),
    ("三", "Three", "初步成形與合作", 1, 0, 1, 0, 1),
    ("四", "Four", "穩定與保守", -1, 1, -1, -1, -1),
    ("五", "Five", "衝突與失衡", 1, -1, -1, 2, 0),
    ("六", "Six", "調整後的回升", 0, 0, 2, -1, 1),
    ("七", "Seven", "堅持與防守反擊", -1, 1, 0, 1, -1),
    ("八", "Eight", "速度與快速轉換", 2, 0, 2, 0, 1),
    ("九", "Nine", "接近極限的爆發", 1, 0, 1, 1, 1),
    ("十", "Ten", "滿載與沉重的負荷", 1, 1, -1, 1, 0),
    ("侍者", "Page", "年輕、經驗不足而充滿變數", -1, 0, 0, 1, 0),
    ("騎士", "Knight", "積極突進的速度型衝擊", 2, 0, 2, 1, 1),
    ("王后", "Queen", "成熟的掌控與調度", 0, 2, 1, -1, 0),
    ("國王", "King", "權威的指揮與壓制", 1, 2, 1, -1, 0),
]


def _build_minor() -> list[Card]:
    cards: list[Card] = []
    for suit, sinfo in _SUITS.items():
        base = sinfo["base"]
        theme = sinfo["theme"]
        reading = sinfo["reading"]
        en_suit = sinfo["en"]
        for rank_zh, rank_en, rank_theme, da, dd, dm, dv, dg in _RANKS:
            attack = _clamp(base["attack"] + da, 0, 10)
            defense = _clamp(base["defense"] + dd, 0, 10)
            momentum = _clamp(base["momentum"] + dm, -5, 5)
            volatility = _clamp(base["volatility"] + dv, 0, 10)
            goal = _clamp(base["goal"] + dg, 0, 10)

            upright = f"{rank_theme};{reading}。"
            reversed_ = f"{rank_theme}受阻、能量逆轉;{reading}的效果打折或走樣。"

            cards.append(Card(
                name=f"{suit}{rank_zh}",
                en_name=f"{rank_en} of {en_suit}",
                arcana="minor",
                suit=suit,
                rank=rank_zh,
                upright=upright,
                reversed=reversed_,
                attack=attack,
                defense=defense,
                momentum=momentum,
                volatility=volatility,
                goal=goal,
            ))
    return cards


def build_deck() -> list[Card]:
    """建立完整的 78 張塔羅牌組(22 大牌 + 56 小牌)。"""
    deck: list[Card] = []
    for name, en, upright, reversed_, a, d, m, v, g in _MAJOR:
        deck.append(Card(
            name=name,
            en_name=en,
            arcana="major",
            suit=None,
            rank=None,
            upright=upright,
            reversed=reversed_,
            attack=float(a),
            defense=float(d),
            momentum=float(m),
            volatility=float(v),
            goal=float(g),
        ))
    deck.extend(_build_minor())
    return deck


FULL_DECK: list[Card] = build_deck()
