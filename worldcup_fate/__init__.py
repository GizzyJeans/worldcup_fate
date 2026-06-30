"""worldcup_fate — 2026 世界杯塔羅占卜系統。

以完整 78 張塔羅牌為基礎,純粹依牌面的客觀數值推導兩隊對戰的:
勝負、讓分／受讓、大小分,以及上下半場的局勢變化。

設計原則:不被主觀強弱、賭盤賠率、過盤率所影響,只忠實於牌面。
"""

from .cards import Card, build_deck, FULL_DECK
from .deck import Deck
from .spread import WORLD_CUP_SPREAD, SpreadPosition
from .interpreter import MatchReading, divine

__all__ = [
    "Card",
    "build_deck",
    "FULL_DECK",
    "Deck",
    "WORLD_CUP_SPREAD",
    "SpreadPosition",
    "MatchReading",
    "divine",
]

__version__ = "1.0.0"
