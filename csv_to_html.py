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
        total_points = 0
        total_possible_points = 0

        for pick in picks:
            series = nhl_api_handler.get_series(pick.series_letter)
            winner = series.get_winner()
            team_status = get_team_status(pick, winner)
            games_status = get_games_status(pick, winner, series.total_games())

            points = get_points(scoring, team_status, games_status)
            total_points += points

            possible_points = points if winner else calculate_possible_points(scoring, series, pick)
            total_possible_points += possible_points

            pick_results.append(PickResult(pick, points, possible_points, team_status, games_status))

        rows.append(Row(person, pick_results, total_points, total_possible_points))

    return rows


def make_html(rows: list[Row], nhl_api_handler: NhlApiHandler) -> str:
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="en"):
        with a.head():
            a.title(_t="Bryan Family Playoff Pool - Round 1")  # TODO
            a.link(href='css/csv_to_html.css', rel='stylesheet')
            a.link(href='css/teams.css', rel='stylesheet')
        with a.body():
            with a.table(klass="containing_table"):
                with a.tr():
                    a.th(_t="Person")
                    for series_letter in nhl_api_handler.get_series_order():
                        series = nhl_api_handler.get_series(series_letter)  # TODO move to nhlapihandler?
                        a.th(_t=series.get_series_summary_html())
                    a.th(_t="Points")
                    a.th(_t="Rank")
                    a.th(_t="Possible Points")

                row_count = 0
                all_points = list(map(lambda r: r.total_points, rows))
                for row in sorted(rows, key=lambda x: x.person):
                    rank = excel_rank(all_points, row.total_points)
                    leader_class = " leader" if rank == 1 else ""
                    with a.tr():
                        a.td(_t=row.person, klass="person" + leader_class)
                        for result in row.pick_results:
                            with a.td():
                                with a.table(klass="pick"):
                                    with a.tr():
                                        with a.td(klass=result.team_status.name.lower()):
                                            with a.div(klass="img_container"):
                                                a.img(src=result.pick.team.logo, alt=result.pick.team.short)
                                        with a.td(klass=result.games_status.name.lower()):
                                            a.span(_t=result.pick.games, klass="games")
                        a.td(_t=row.total_points, klass="points" + leader_class)
                        a.td(_t=rank, klass="rank" + leader_class)
                        a.td(_t=row.possible_points, klass="possible_points")
                    row_count += 1
    return str(a)


def excel_rank(values, target):
    sorted_values = sorted(values, reverse=True)
    try:
        return sorted_values.index(target) + 1
    except ValueError:
        return None


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


def get_games_status(pick: Pick, winner: Winner, games_played: int) -> PickStatus:
    # sometimes we can assign correctness early
    if winner is None:
        # since we know the 7th game will be the last we can give points early
        if games_played == 6 and pick.games == 7:
            return PickStatus.CORRECT
        # if >= games than the guess have been played, it's a bad guess
        if games_played >= pick.games:
            return PickStatus.INCORRECT
    return get_pick_status(
        pick,
        winner,
        lambda p, w: p.games == w.games
    )


def get_points(scoring: Scoring, team_status: PickStatus, games_status: PickStatus) -> int:
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
