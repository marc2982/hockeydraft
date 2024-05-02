#!/usr/bin/env python3
import csv
from datetime import datetime
import sys
from enum import Enum

from airium import Airium

from common import Scoring, Winner, Pick, PickResult, Row
from nhl_api_handler import NhlApiHandler


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


def read_csv(csv_filename):
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        return [row for row in reader]


def read_picks_round1(rows: list[Row], nhl_api_handler: NhlApiHandler) -> dict[str, list[Pick]]:
    # !!!2024 hack only!!!
    # since the form doesnt follow the letter order that the api does, hardcode the order of the first round
    if nhl_api_handler.year == 2024:  # TODO: round 1 only
        series_order = ["G", "H", "A", "B", "C", "D", "E", "F"]
    else:
        series_order = ["A", "B", "C", "D", "E", "F", "G", "H"]

    trs = {}
    for row in rows:
        tds = []
        person = row[1]
        col_iter = iter(row[2:])

        i = 0
        for col in col_iter:
            team_name = col
            num_games = next(col_iter)

            pick = Pick(
                series_letter=series_order[i],
                team=nhl_api_handler.get_team(team_name),
                games=int(num_games)
            )

            tds.append(pick)
            i += 1

        trs[person] = tds
    return trs


def build_data(
        scoring: Scoring,
        nhl_api_handler: NhlApiHandler,
        picks_by_person: dict[str, list[Pick]]
        ) -> list[Row]:
    rows = []

    for person, picks in picks_by_person.items():
        pick_results = []

        for pick in picks:
            winner = nhl_api_handler.get_series(pick.series_letter).get_winner()
            team_status = get_team_status(pick, winner)
            games_status = get_games_status(pick, winner)
            points = get_points(scoring, team_status, games_status)
            possible_points = calculate_possible_points(scoring, winner, points)
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
            a.link(href='teams.css', rel='stylesheet')
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

                            with a.td(klass=result.pick.team.short):
                                with a.table(klass="pick"):
                                    with a.tr():
                                        with a.td():
                                            a.img(src=result.pick.team.logo, alt=result.pick.team.short)
                                        with a.td(klass="result"):
                                            a.span(klass=result.team_status.name.lower())
                                    with a.tr():
                                        a.td(_t=result.pick.games, klass="games")
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
        lambda p, w: p.team.short == w.team.short
    )


def get_games_status(pick: Pick, winner: Winner) -> PickStatus:
    return get_pick_status(
        pick,
        winner,
        lambda p, w: p.games == w.games
    )


def get_points(scoring: Scoring, team_status: PickStatus, games_status: PickStatus) -> int:
    if team_status == PickStatus.UNKNOWN or games_status == PickStatus.UNKNOWN:
        return 0
    correct_team = team_status == PickStatus.CORRECT
    correct_games = games_status == PickStatus.CORRECT
    points = 0
    points += scoring.team if correct_team else 0
    points += scoring.games if correct_games else 0
    points += scoring.bonus if correct_team and correct_games else 0
    return points


def calculate_possible_points(scoring: Scoring, winner: Winner, current_points: int) -> int:
    if not winner:
        return scoring.team + scoring.games + scoring.bonus
    # TODO: do more here now
    return current_points


def write_html(html, filename):
    with open(filename, 'w') as f:
        for row in html:
            f.write(row)


def main(argv):
    round_scoring = SCORING[0]  # TODO
    rows = read_csv(argv[1])

    year = datetime.now().year  # TODO
    nhl_api_handler = NhlApiHandler(year)
    nhl_api_handler.load()

    picks_by_person = read_picks_round1(rows, nhl_api_handler)
    rows = build_data(round_scoring, nhl_api_handler, picks_by_person)
    html = make_html(rows)
    write_html(html, "round1.html")


if __name__ == "__main__":
    main(sys.argv)
