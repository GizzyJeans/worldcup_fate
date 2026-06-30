"""命令列介面:為一場 2026 世界杯對戰占卜。

範例:
    python -m worldcup_fate 阿根廷 法國
    python -m worldcup_fate 西班牙 德國 --stage 八強 --date 2026-07-04
    python -m worldcup_fate 巴西 英格蘭 --json
"""

from __future__ import annotations

import argparse
import json
import sys

from .interpreter import divine
from .report import render


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="worldcup_fate",
        description="2026 世界杯塔羅占卜系統 —— 以塔羅牌客觀預言兩隊對戰走勢。",
    )
    p.add_argument("home", help="主隊名稱(先列出的隊伍)")
    p.add_argument("away", help="客隊名稱(後列出的隊伍)")
    p.add_argument("--stage", default="小組賽",
                   help="賽事階段,例如:小組賽 / 十六強 / 八強 / 準決賽 / 決賽")
    p.add_argument("--date", default=None,
                   help="比賽日期 (YYYY-MM-DD);省略則用今日,影響命運種子")
    p.add_argument("--json", action="store_true",
                   help="以 JSON 輸出機讀結果,而非占卜報告")
    return p


def _to_dict(reading) -> dict:
    return {
        "home": reading.home,
        "away": reading.away,
        "stage": reading.stage,
        "date": reading.date,
        "winner": reading.winner,
        "predicted_score": list(reading.predicted_score),
        "predicted_total": reading.predicted_total,
        "confidence": reading.confidence,
        "predictions": {
            "win": reading.win_text,
            "handicap": reading.handicap_text,
            "totals": reading.totals_text,
            "halves": reading.halves_text,
        },
        "cards": {
            key: {
                "name": dc.card.name,
                "en_name": dc.card.en_name,
                "reversed": dc.reversed,
                "meaning": dc.meaning,
            }
            for key, dc in reading.cards.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    reading = divine(args.home, args.away, stage=args.stage, date=args.date)

    if args.json:
        print(json.dumps(_to_dict(reading), ensure_ascii=False, indent=2))
    else:
        print(render(reading))
    return 0


if __name__ == "__main__":
    sys.exit(main())
