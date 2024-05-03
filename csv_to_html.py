#!/usr/bin/env python3
import csv
from datetime import datetime
import sys
from enum import Enum

from airium import Airium

from common import Scoring, Winner, Pick, PickResult, Row, Series
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
    series_order = nhl_api_handler.get_series_order()

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
            series = nhl_api_handler.get_series(pick.series_letter)
            winner = series.get_winner()
            team_status = get_team_status(pick, winner)
            games_status = get_games_status(pick, winner)
            points = get_points(scoring, team_status, games_status)
            possible_points = points if winner else calculate_possible_points(scoring, series, pick)
            pick_results.append(PickResult(pick, points, possible_points, team_status, games_status))

        rows.append(Row(person, pick_results))

    return rows


def make_html(rows: list[Row], nhl_api_handler: NhlApiHandler) -> str:
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.title(_t="Bryan Family Playoff Pool - Round 1")  # TODO
            a.link(href='csv_to_html.css', rel='stylesheet')
            a.link(href='teams.css', rel='stylesheet')
        with a.body():
            with a.table(style="padding: 1px;"):
                with a.tr():
                    a.th(_t="Person")
                    for series_letter in nhl_api_handler.get_series_order():
                        series = nhl_api_handler.get_series(series_letter)  # TODO move to nhlapihandler?
                        a.th(_t=series.get_series_summary())
                    a.th(_t="Points")
                    a.th(_t="Possible Points")
                for row in sorted(rows, key=lambda x: x.person):
                    total_points = 0
                    possible_points = 0

                    with a.tr():
                        a.td(_t=row.person, style="font-weight: bold;")
                        for result in row.pick_results:
                            total_points += result.points
                            possible_points += result.possible_points

                            with a.td():
                                with a.table(klass="pick"):
                                    with a.tr():
                                        with a.td(klass=f"{result.pick.team.short} {result.team_status.name.lower()}"):
                                            a.img(src=result.pick.team.logo, alt=result.pick.team.short)
                                            with a.span(klass="cover-checkbox"):
                                                with a.svg(viewBox="0 0 12 10"):
                                                    a.polyline(points="1.5 6 4.5 9 10.5 1")
                                        with a.td(klass="result"):
                                            a.span(_t=result.pick.games, klass=f"games {result.games_status.name.lower()}")
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


# this function should ONLY be called when there is no winner
def calculate_possible_points(scoring: Scoring, series: Series, pick: Pick) -> int:
    possible_from_team = scoring.team
    possible_from_games = scoring.games if pick.games > series.total_games() else 0
    possible_from_bonus = scoring.bonus if possible_from_games > 0 else 0
    return possible_from_team + possible_from_games + possible_from_bonus


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
    html = make_html(rows, nhl_api_handler)
    write_html(html, "round1.html")


if __name__ == "__main__":
    main(sys.argv)
