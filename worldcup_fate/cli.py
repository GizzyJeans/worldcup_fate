"""命令列介面:為一場 2026 世界杯對戰占卜。

範例:
    python -m worldcup_fate 阿根廷 法國
    python -m worldcup_fate 西班牙 德國 --stage 八強 --date 2026-07-04
    python -m worldcup_fate 巴西 英格蘭 --json

    # 自動查表:依隊名帶入已查證的階段/日期/場館再開牌
    python -m worldcup_fate 西班牙 奧地利 --auto

    # 列出已收錄的賽程
    python -m worldcup_fate --list-fixtures
"""

from __future__ import annotations

import argparse
import json
import sys

from .interpreter import divine
from .report import render
from . import fixtures


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="worldcup_fate",
        description="2026 世界杯塔羅占卜系統 —— 以塔羅牌客觀預言兩隊對戰走勢。",
    )
    p.add_argument("home", nargs="?", help="主隊名稱(先列出的隊伍)")
    p.add_argument("away", nargs="?", help="客隊名稱(後列出的隊伍)")
    p.add_argument("--stage", default=None,
                   help="賽事階段,例如:小組賽 / 32強淘汰賽 / 十六強 / 八強 / 準決賽 / 決賽")
    p.add_argument("--date", default=None,
                   help="比賽日期 (YYYY-MM-DD);省略則用今日,影響命運種子")
    p.add_argument("--auto", action="store_true",
                   help="依隊名自動查表帶入已查證的階段/日期/場館(查無則沿用手動值)")
    p.add_argument("--list-fixtures", action="store_true",
                   help="列出已收錄的賽程後結束")
    p.add_argument("--json", action="store_true",
                   help="以 JSON 輸出機讀結果,而非占卜報告")
    return p


def _print_fixtures() -> None:
    print("已收錄賽程(整理自公開來源,以 FIFA 官方為準):")
    print("-" * 60)
    for fx in fixtures.iter_fixtures():
        a, b = fx["teams"]
        print(f"◆ {a} vs {b}")
        print(f"    階段:{fx['stage']}　日期:{fx['date']}　開賽:{fx['kickoff']}")
        print(f"    場館:{fx['venue']}")
    print("-" * 60)


def _to_dict(reading) -> dict:
    return {
        "home": reading.home,
        "away": reading.away,
        "stage": reading.stage,
        "date": reading.date,
        "venue": reading.venue,
        "kickoff": reading.kickoff,
        "winner": reading.winner,
        "knife_edge": reading.knife_edge,
        "overtime_risk": reading.overtime_risk,
        "handicap_line": reading.handicap_line,
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
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.list_fixtures:
        _print_fixtures()
        return 0

    if not args.home or not args.away:
        parser.error("請提供主隊與客隊名稱(或使用 --list-fixtures 查看賽程)。")

    stage = args.stage
    date = args.date
    venue = kickoff = source = ""

    if args.auto:
        fx = fixtures.find_fixture(args.home, args.away)
        if fx is None:
            print(f"⚠ 賽程資料集中查無「{args.home} vs {args.away}」,沿用手動/預設值。",
                  file=sys.stderr)
        else:
            # 自動帶入賽程資訊;命令列若已明確指定則以命令列優先
            stage = stage or fx["stage"]
            date = date or fx["date"]
            venue = fx["venue"]
            kickoff = fx["kickoff"]
            source = fx["source"]

    if stage is None:
        stage = "小組賽"

    reading = divine(args.home, args.away, stage=stage, date=date,
                     venue=venue, kickoff=kickoff, source=source)

    if args.json:
        print(json.dumps(_to_dict(reading), ensure_ascii=False, indent=2))
    else:
        print(render(reading))
    return 0


if __name__ == "__main__":
    sys.exit(main())
