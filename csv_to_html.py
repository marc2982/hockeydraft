#!/usr/bin/env python3
import csv
import sys
from collections import namedtuple
from enum import Enum

from airium import Airium


Team = namedtuple("Team", "short colour img")
Pick = namedtuple("Pick", "team games")
Winner = namedtuple("Winner", "team games")
Scoring = namedtuple("Scoring", "team games bonus")
Row = namedtuple("Row", "person pick_results")
PickResult = namedtuple("PickResult", "pick points possible_points team_status games_status")

PickStatus = Enum("PickStatus", [
    "CORRECT",
    "INCORRECT",
    "UNKNOWN"
])

SCORING = [
    Scoring(1, 2, 3),
    Scoring(2, 3, 4),
    Scoring(3, 4, 5),
    Scoring(4, 5, 6)
]

DATA = {
    "Boston Bruins (A2)": Team("BOS", "000000", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/6.svg"),
    "Carolina Hurricanes (M2)": Team("CAR", "CE1126", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/12.svg"),
    "Colorado Avalanche (C3)": Team("COL", "6F263D", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/21.svg"),
    "Dallas Stars (C1)": Team("DAL", "006847", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/25.svg"),
    "Edmonton Oilers (P2)": Team("EDM", "FF4C00", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/22.svg"),
    "Florida Panthers (A1)": Team("FLA", "C8102E", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/13.svg"),
    "Los Angeles Kings (P3)": Team("LAK", "111111", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/26.svg"),
    "Nashville Predators (WC1)": Team("NAS", "FFB81C", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/18.svg"),
    "New York Islanders (M3)": Team("NYI", "F47D30", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/2.svg"),
    "New York Rangers (M1)": Team("NYR", "0038A8", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/3.svg"),
    "Tampa Bay Lightning (WC1)": Team("TBL", "002469", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/14.svg"),
    "Toronto Maple Leafs (A3)": Team("TOR", "00205B", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/10.svg"),
    "Vancouver Canucks (P1)": Team("VAN", "00843D", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/23.svg"),
    "Vegas Golden Knights (WC2)": Team("VGK", "B4975A", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/54.svg"),
    "Washington Capitals (WC2)": Team("WAS", "C8102E", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/15.svg"),
    "Winnipeg Jets (C2)": Team("WSH", "55565A", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/52.svg")
}

WINNERS = [
    None,
    None,
    Winner("FLA", 5),
    None,
    Winner("NYR", 4),
    Winner("CAR", 5),
    None,
    Winner("COL", 5)
]


def read_csv(csv_filename):
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        return [row for row in reader]


def read_picks_round1(rows):
    trs = {}
    for row in rows:
        tds = []
        person = row[1]
        col_iter = iter(row[2:])

        for col in col_iter:
            team_name = col
            num_games = next(col_iter)

            pick = Pick(
                team=DATA[team_name],
                games=int(num_games)
            )

            tds.append(pick)
        trs[person] = tds
    return trs


def build_data(scoring: Scoring, trs: map) -> list[Row]:
    rows = []

    for person in trs.keys():
        picks = trs[person]
        pick_results = []

        for (i, pick) in enumerate(picks):
            winner = WINNERS[i]
            scoring = SCORING[0]  # TODO
            points = get_points(scoring, pick, winner)
            possible_points = calculate_possible_points(scoring, pick, winner)
            team_status = get_team_status(pick, winner)
            games_status = get_games_status(pick, winner)
            pick_results.append(PickResult(pick, points, possible_points, team_status, games_status))

        rows.append(Row(person, pick_results))

    return rows


def make_html(rows: list[Row]) -> str:
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.title(_t="Bryan Family Playoff Pool - Round 1")  # TODO
            a.link(href='csv_to_html.css', rel='stylesheet')
        with a.body():
            with a.table(style="padding: 5px;"):
                for row in sorted(rows, key=lambda x: x.person):
                    total_points = 0
                    possible_points = 0

                    with a.tr():
                        a.td(_t=row.person, style="font-weight: bold;")
                        for result in row.pick_results:
                            total_points += result.points
                            possible_points += result.possible_points

                            with a.td(style=f"background-color: #{result.pick.team.colour};"):
                                with a.table(klass="pick"):
                                    with a.tr():
                                        with a.td():
                                            a.img(src=result.pick.team.img, alt=result.pick.team.short)
                                        with a.td():
                                            a.span(klass=result.team_status.name.lower())
                                    with a.tr():
                                        a.td(_t=result.pick.games, style=f"color: #000000; font-weight: bold;")
                                        with a.td():
                                            a.span(klass=result.games_status.name.lower())
                        a.td(_t=total_points)
                        a.td(_t=possible_points)

    return str(a)


def get_pick_status(pick: Pick, winner: Winner, predicate: callable) -> PickStatus:
    if not winner:
        return PickStatus.UNKNOWN
    if predicate(pick, winner):
        return PickStatus.CORRECT
    return PickStatus.INCORRECT


def get_team_status(pick: Pick, winner: Winner) -> PickStatus:
    return get_pick_status(
        pick,
        winner,
        lambda p, w: p.team.short == w.team
    )


def get_games_status(pick: Pick, winner: Winner):
    return get_pick_status(
        pick,
        winner,
        lambda p, w: p.games == w.games
    )


def get_points(scoring: Scoring, pick: Pick, winner: Winner) -> int:
    if not winner:
        return 0
    correct_team = pick.team.short == winner.team
    correct_games = pick.games == winner.games
    points = 0
    points += scoring.team if correct_team else 0
    points += scoring.games if correct_games else 0
    points += scoring.bonus if correct_team and correct_games else 0
    return points


def calculate_possible_points(scoring: Scoring, pick: Pick, winner: Winner) -> int:
    if not winner:
        return scoring.team + scoring.games + scoring.bonus
    return get_points(scoring, pick, winner)


def write_html(html, filename):
    with open(filename, 'w') as f:
        for row in html:
            f.write(row)


def main(argv):
    round_scoring = SCORING[0]  # TODO
    rows = read_csv(argv[1])
    trs = read_picks_round1(rows)
    rows = build_data(round_scoring, trs)
    html = make_html(rows)
    write_html(html, "round1.html")


if __name__ == "__main__":
    main(sys.argv)

