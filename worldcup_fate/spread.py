"""世界杯戰局牌陣 (七張牌牌陣)。

每個位置對應比賽的一個面向,抽出的牌在該位置上的能量,構成占卜引擎
推導勝負、讓分、大小分與上下半場走勢的素材。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpreadPosition:
    key: str
    name: str
    description: str


WORLD_CUP_SPREAD: list[SpreadPosition] = [
    SpreadPosition("home", "主隊根基",
                   "代表主隊(先列出的隊伍)的整體狀態與攻守能量。"),
    SpreadPosition("away", "客隊根基",
                   "代表客隊(後列出的隊伍)的整體狀態與攻守能量。"),
    SpreadPosition("first_half", "上半場之相",
                   "揭示開賽至中場的節奏、氣勢與進球傾向。"),
    SpreadPosition("second_half", "下半場之相",
                   "揭示易邊再戰後的局勢演變與體能消長。"),
    SpreadPosition("total_goals", "進球之潮",
                   "象徵全場進球的總體強度,是大小分的核心依據。"),
    SpreadPosition("wildcard", "關鍵變數",
                   "潛伏的不確定因素:傷病、判罰、紅黃牌與爆冷的伏筆。"),
    SpreadPosition("verdict", "最終定論",
                   "凌駕全局的總結之牌,定調最終結果的成色與信心。"),
]

POSITION_COUNT = len(WORLD_CUP_SPREAD)
