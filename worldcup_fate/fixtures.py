"""已查證的 2026 世界杯賽程資料集與查表功能。

由於直接在程式中即時爬取 FIFA／新聞網站並不可靠(多數站點會以 403 阻擋
爬蟲,一般使用者環境亦未必能連線),本模組改採更穩健的做法:內建一份
「已查證」的賽程資料,占卜時可依隊名自動帶入正確的階段、日期與場館。

⚠️ 資料來源與時效:以下賽程整理自 2026 年 7 月的公開報導(見各筆 source),
   僅供對照,最終請以 FIFA 官方賽程為準。若賽程有異或需擴充,直接編輯
   FIXTURES 清單即可(欄位格式見下)。

每筆賽程欄位:
    stage    : 賽事階段(與占卜命運種子一致的中文字串)
    date     : 比賽日期 YYYY-MM-DD(納入命運種子)
    kickoff  : 開賽時間(僅供顯示)
    venue    : 場館與城市(僅供顯示)
    teams    : [隊伍A, 隊伍B] 的標準英文名(查表用,順序不拘)
    source   : 資料出處
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# 隊名對照:中文／變體 -> 標準英文名
# --------------------------------------------------------------------------- #
_TEAM_ALIASES: dict[str, str] = {
    # 已收錄賽程涉及的隊伍
    "西班牙": "Spain", "spain": "Spain",
    "奧地利": "Austria", "奥地利": "Austria", "austria": "Austria",
    "葡萄牙": "Portugal", "portugal": "Portugal",
    "克羅埃西亞": "Croatia", "克罗地亚": "Croatia", "croatia": "Croatia",
    "阿根廷": "Argentina", "argentina": "Argentina",
    "維德角": "Cape Verde", "佛得角": "Cape Verde", "cape verde": "Cape Verde",
    # 其他常見隊伍(方便使用者以中文輸入)
    "法國": "France", "法国": "France", "france": "France",
    "瑞典": "Sweden", "sweden": "Sweden",
    "墨西哥": "Mexico", "mexico": "Mexico",
    "厄瓜多": "Ecuador", "厄瓜多爾": "Ecuador", "ecuador": "Ecuador",
    "象牙海岸": "Ivory Coast", "科特迪瓦": "Ivory Coast",
    "cote d'ivoire": "Ivory Coast", "ivory coast": "Ivory Coast",
    "挪威": "Norway", "norway": "Norway",
    "巴西": "Brazil", "brazil": "Brazil",
    "英格蘭": "England", "英格兰": "England", "england": "England",
    "德國": "Germany", "德国": "Germany", "germany": "Germany",
    "荷蘭": "Netherlands", "荷兰": "Netherlands", "netherlands": "Netherlands",
    "日本": "Japan", "japan": "Japan",
    "美國": "USA", "美国": "USA", "usa": "USA", "united states": "USA",
    "摩洛哥": "Morocco", "morocco": "Morocco",
    "瑞士": "Switzerland", "switzerland": "Switzerland",
    "阿爾及利亞": "Algeria", "阿尔及利亚": "Algeria", "algeria": "Algeria",
    "澳洲": "Australia", "澳大利亞": "Australia", "澳大利亚": "Australia",
    "australia": "Australia",
    "埃及": "Egypt", "egypt": "Egypt",
    "哥倫比亞": "Colombia", "哥伦比亚": "Colombia", "colombia": "Colombia",
    "迦納": "Ghana", "加納": "Ghana", "加纳": "Ghana", "ghana": "Ghana",
    "加拿大": "Canada", "canada": "Canada",
    "巴拉圭": "Paraguay", "paraguay": "Paraguay",
}

# --------------------------------------------------------------------------- #
# 已查證賽程(2026 世界杯 32 強淘汰賽,整理自公開報導)
# --------------------------------------------------------------------------- #
FIXTURES: list[dict] = [
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-02",
        "kickoff": "12:00 PT / 15:00 ET / 19:00 GMT",
        "venue": "SoFi Stadium, Inglewood(洛杉磯)",
        "teams": ["Spain", "Austria"],
        "source": "https://www.fifa.com/en/match-centre/match/17/285023/289287/400021519",
    },
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-02",
        "kickoff": "19:00 ET(場地當地)",
        "venue": "BMO Field, Toronto",
        "teams": ["Portugal", "Croatia"],
        "source": "https://www.skysports.com/football/news/12098/13556636/world-cup-2026-bracket-and-knockout-fixtures-whos-facing-who-in-the-last-32-and-route-to-final",
    },
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-03",
        "kickoff": "18:00 ET(場地當地)",
        "venue": "Hard Rock Stadium, Miami Gardens",
        "teams": ["Argentina", "Cape Verde"],
        "source": "https://sports.yahoo.com/soccer/article/world-cup-2026-round-of-32-full-bracket-matchups-schedule-and-how-each-team-qualified-164942403.html",
    },
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-02",
        "kickoff": "20:00 PT / 23:00 ET",
        "venue": "BC Place, Vancouver",
        "teams": ["Switzerland", "Algeria"],
        "source": "https://www.espn.com/soccer/story/_/id/49223711/fifa-world-cup-2026-switzerland-vs-algeria-tv-channel-how-watch-kickoff-live-stream-referee-predicted-lineups",
    },
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-03",
        "kickoff": "14:00 CT(場地當地)",
        "venue": "AT&T Stadium, Arlington(達拉斯)",
        "teams": ["Australia", "Egypt"],
        "source": "https://socceroos.com.au/news/how-watch-australia-vs-egypt-fifa-world-cup-2026tm-round-32",
    },
    {
        "stage": "32強淘汰賽",
        "date": "2026-07-03",
        "kickoff": "21:30 ET / 18:30 PT",
        "venue": "Arrowhead Stadium(Kansas City Stadium), Kansas City",
        "teams": ["Colombia", "Ghana"],
        "source": "https://www.espn.com/espn/story/_/id/49224579/colombia-vs-ghana-kick-team-news-how-watch-world-cup-round-32-clash",
    },
    {
        "stage": "十六強",
        "date": "2026-07-04",
        "kickoff": "12:00 CT / 17:00 GMT",
        "venue": "Houston Stadium(NRG Stadium), Houston",
        "teams": ["Canada", "Morocco"],
        "source": "https://www.aljazeera.com/sports/2026/7/3/canada-morocco-fifa-world-cup-round-of-16-saibari-prediction-schedule",
    },
    {
        "stage": "十六強",
        "date": "2026-07-04",
        "kickoff": "17:00 ET / 21:00 GMT",
        "venue": "Philadelphia Stadium(Lincoln Financial Field), Philadelphia",
        "teams": ["Paraguay", "France"],
        "source": "https://www.aljazeera.com/sports/2026/7/4/france-vs-paraguay-world-cup-round-of-16-mbappe-prediction-kickoff",
    },
]


def normalize_team(name: str) -> str:
    """把使用者輸入的隊名(中文或英文)正規化為標準英文名。

    找不到對照時,回傳去除前後空白後的原字串(仍可用於比對與顯示)。
    """
    key = name.strip().lower()
    if key in _TEAM_ALIASES:
        return _TEAM_ALIASES[key]
    # 也允許直接輸入標準英文名(不分大小寫)
    for canonical in set(_TEAM_ALIASES.values()):
        if key == canonical.lower():
            return canonical
    return name.strip()


def find_fixture(team_a: str, team_b: str) -> dict | None:
    """依兩隊隊名(順序不拘)查出已收錄的賽程,查無則回傳 None。"""
    want = {normalize_team(team_a), normalize_team(team_b)}
    for fx in FIXTURES:
        if {normalize_team(t) for t in fx["teams"]} == want:
            return fx
    return None


def iter_fixtures() -> list[dict]:
    """回傳所有已收錄的賽程(供列表顯示)。"""
    return list(FIXTURES)
