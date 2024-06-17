#!/usr/bin/env python3
import csv
import os
import sys

from .common import Scoring, Winner, Pick, PickResult, PickStatus, Row, SummaryRow
from .leader_calculator import LeaderCalculator
from .html_generator import HtmlGenerator
from .nhl_api_handler import NhlApiHandler
from .series import Series, ALL_SERIES

PEOPLE = [
    'Benedict',
    'Chrissy',
    'Derrick',
    'Glenda',
    'Jaclyn',
    'Jake',
    'Jamie',
    'Kiersten',
    'Marc',
    'Nathan',
    'Nickall',
    'Robin',
    'Ryan',
    'Sophie',
    'Stephanie',
    'Theodore'
]

SCORING = [
    Scoring(1, 2, 3),
    Scoring(2, 3, 4),
    Scoring(3, 4, 5),
    Scoring(4, 5, 6)
]


def read_csv(csv_filename: str, skip_headers: bool) -> list:
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        if skip_headers:
            next(reader, None)  # skip the headers
        return [row for row in reader]


def read_old_picks(
        rows: list[Row],
        nhl_api_handler: NhlApiHandler,
        year: int,
        round: int
        ) -> dict[str, list[Pick]]:
    series_order = get_series_import_order(year, round)

    trs = {}
    for row in rows:
        tds = []

        person = row[0]
        if person.lower() == "dad":
            person = "Derrick"
        elif person.lower() in ["mom", "chris"]:
            person = "Chrissy"
        elif person.lower() == "m.c.b.":
            person = "Marc"

        col_iter = iter(row[1:])

        i = 0
        for col in col_iter:
            raw_team, num_games = map(lambda r: r.strip(), col.split("-"))
            team_name = strip_rank(raw_team)

            pick = Pick(
                series_letter=series_order[i],
                team=nhl_api_handler.get_team(team_name),
                games=int(num_games)
            )

            tds.append(pick)
            i += 1

        trs[person] = tds
    return trs


def read_picks(
    rows: list[Row],
    nhl_api_handler: NhlApiHandler,
    year: int,
    round: int
) -> dict[str, list[Pick]]:
    series_order = get_series_import_order(year, round)

    trs = {}
    for row in rows:
        tds = []
        person = row[1]
        col_iter = iter(row[2:])

        i = 0
        for col in col_iter:
            team_name = strip_rank(col)
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


# !!!HACK ALERT!!!
# since previous forms dont follow the letter order that the api does,
# hardcode the order the picks are in. Future years should match
def get_series_import_order(year: int, round: int) -> list[str]:
    pick_order = ALL_SERIES
    if year == 2024:
        pick_order = [
            ['G', 'H', 'A', 'B', 'C', 'D', 'E', 'F'],
            ['I', 'J', 'K', 'L'],
            ['M', 'N'],
            ['O']
        ]
    elif year == 2023:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2022:
        pick_order = [
            ['G', 'H', 'A', 'B', 'C', 'D', 'E', 'F'],
            ['K', 'I', 'J', 'L'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2021:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'I', 'J', 'L'],
            ['M', 'N'],
            ['O']
        ]
    elif year == 2020:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['L', 'K', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2019:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['L', 'K', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2018:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2017:
        pick_order = [
            ['E', 'F', 'H', 'G', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2016:
        pick_order = [
            ['E', 'F', 'G', 'H', 'C', 'D', 'A', 'B'],
            ['K', 'L', 'J', 'I'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2015:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2014:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2010:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2009:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2008:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2007:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'J', 'I'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2006:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2004:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['L', 'K', 'J', 'I'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2003:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2002:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2001:
        pick_order = [
            ['F', 'G', 'E', 'H', 'D', 'C', 'B', 'A'],
            ['L', 'K', 'J', 'I'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 2000:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 1999:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 1998:
        pick_order = [
            ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D'],
            ['K', 'L', 'I', 'J'],
            ['N', 'M'],
            ['O']
        ]
    elif year == 1997:
        pick_order = [
            ['D', 'C', 'B', 'A', 'H', 'E', 'G', 'F'],
            ['I', 'J', 'K', 'L'],
            ['M', 'N'],
            ['O']
        ]
    return pick_order[round - 1]


def strip_rank(team_name: str) -> str:
    i = team_name.find('(')
    if i == -1:
        return team_name
    return team_name[:i-1]  # strip the end, including the space before (


def build_data(
        scoring: Scoring,
        nhl_api_handler: NhlApiHandler,
        picks_by_person: dict[str, list[Pick]],
        series_letters: list[str]
        ) -> list[Row]:
    rows = []

    for person, picks in picks_by_person.items():
        pick_results = []
        total_points = 0
        total_possible_points = 0

        for series_letter in series_letters:
            pick = next(p for p in picks if p.series_letter == series_letter)
            series = nhl_api_handler.get_series(pick.series_letter)

            winner = series.get_winner()
            team_status = get_team_status(pick, winner)
            games_status = get_games_status(pick, winner, series)

            points = get_points(scoring, team_status, games_status)
            total_points += points

            possible_points = points if winner else calculate_possible_points(scoring, team_status, games_status)
            total_possible_points += possible_points

            p = PickResult(series.letter, pick, points, possible_points, team_status, games_status)
            pick_results.append(p)

        rows.append(Row(person.capitalize(), pick_results, total_points, total_possible_points))

    return rows


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


def get_games_status(pick: Pick, winner: Winner, series: Series) -> PickStatus:
    # sometimes we can assign correctness early
    if winner is None:
        games_played = series.total_games()
        # since we know the 7th game will be the last we can give points early
        if games_played == 6 and pick.games == 7:
            return PickStatus.CORRECT
        # if >= games than the guess have been played, it's a bad guess
        if games_played >= pick.games:
            return PickStatus.INCORRECT
        # certain games become impossible, ie both teams win 1 each so 4 games is impossible
        min_games_for_winner = min(series.top_seed_wins, series.bottom_seed_wins) + 4
        if pick.games < min_games_for_winner:
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
def calculate_possible_points(scoring: Scoring, team_status: PickStatus, games_status: PickStatus) -> int:
    possible_from_team = scoring.team if team_status in [PickStatus.CORRECT, PickStatus.UNKNOWN] else 0
    possible_from_games = scoring.games if games_status in [PickStatus.CORRECT, PickStatus.UNKNOWN] else 0
    possible_from_bonus = scoring.bonus if possible_from_team > 0 and possible_from_games > 0 else 0
    return possible_from_team + possible_from_games + possible_from_bonus


def write_html(html, filename):
    with open(filename, 'w') as f:
        for row in html:
            f.write(row)


def main(folder_name: str) -> tuple[str, str]:
    year = int(folder_name.rstrip('/'))
    nhl_api_handler = NhlApiHandler(year)
    nhl_api_handler.load()

    all_rows = []
    for i in range(4):  # 4 rounds in the playoffs
        round = i + 1
        round_scoring = SCORING[i]
        file_path = os.path.join(folder_name, f'round{round}.csv')
        if os.path.exists(file_path):
            if year < 2008:
                csv_rows = read_csv(file_path, False)
                picks_by_person = read_old_picks(csv_rows, nhl_api_handler, year, round)
            else:
                csv_rows = read_csv(file_path, True)
                picks_by_person = read_picks(csv_rows, nhl_api_handler, year, round)
            round_rows = build_data(round_scoring, nhl_api_handler, picks_by_person, ALL_SERIES[i])
            all_rows.append(round_rows)
        else:
            round_rows = []
            for person in PEOPLE:
                round_rows.append(Row(
                    person,
                    [PickResult(series_letter, None, 0, 0, PickStatus.UNKNOWN, PickStatus.UNKNOWN)
                     for series_letter in ALL_SERIES[i]
                     ],
                    0,
                    0
                ))
            all_rows.append(round_rows)

    html = HtmlGenerator(
        nhl_api_handler,
        all_rows
    ).make_html(SCORING, year)
    out_path = os.path.join(folder_name, 'index.html')
    return html, out_path


if __name__ == '__main__':
    main(sys.argv[1])
