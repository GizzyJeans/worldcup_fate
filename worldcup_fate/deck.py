"""牌組:洗牌與抽牌。

核心理念是「命運種子」:給定相同的對戰組合、賽事階段與日期,洗出的牌序
與正逆位完全固定、無法重抽。這確保占卜結果只取決於命運本身,而非占卜者
反覆重洗以規避不想要的結果。
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from .cards import Card, FULL_DECK


@dataclass(frozen=True)
class DrawnCard:
    """一張已抽出、已定正逆位的牌。"""

    card: Card
    reversed: bool

    @property
    def orientation(self) -> str:
        return "逆位" if self.reversed else "正位"

    @property
    def meaning(self) -> str:
        return self.card.reversed if self.reversed else self.card.upright


def _seed_from(*parts: str) -> int:
    """以對戰資訊雜湊出可重現的整數種子。"""
    raw = "|".join(p.strip() for p in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(digest, 16) % (2 ** 32)


class Deck:
    """一副可依命運種子洗牌、抽牌的塔羅牌組。"""

    REVERSED_PROBABILITY = 0.5

    def __init__(self, cards: list[Card] | None = None, seed: int | None = None):
        self._cards = list(cards if cards is not None else FULL_DECK)
        self._rng = random.Random(seed)

    @classmethod
    def for_match(cls, home: str, away: str, stage: str, date: str) -> "Deck":
        """為一場特定對戰建立牌組(命運種子由對戰資訊決定)。"""
        seed = _seed_from(home, away, stage, date)
        return cls(seed=seed)

    def shuffle(self) -> None:
        self._rng.shuffle(self._cards)

    def draw(self, count: int) -> list[DrawnCard]:
        """洗牌後抽出 count 張牌,並為每張牌決定正逆位。"""
        if count > len(self._cards):
            raise ValueError(f"牌組僅有 {len(self._cards)} 張,無法抽出 {count} 張。")
        self.shuffle()
        drawn: list[DrawnCard] = []
        for card in self._cards[:count]:
            is_reversed = self._rng.random() < self.REVERSED_PROBABILITY
            drawn.append(DrawnCard(card=card, reversed=is_reversed))
        return drawn
