#!/usr/bin/env python3
from enum import Enum
import csv
import os
import sys

from airium import Airium

from .common import Scoring, Winner, Pick, PickResult, Row, SummaryRow
from .nhl_api_handler import NhlApiHandler
from .series import Series, ALL_SERIES

PEOPLE = [
    'Benedict',
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

PickStatus = Enum('PickStatus', [
    'CORRECT',
    'INCORRECT',
    'UNKNOWN'
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

        rows.append(Row(person, pick_results, total_points, total_possible_points))

    return rows


def make_html(all_rows: list[list[Row]], nhl_api_handler: NhlApiHandler, scoring: list[Scoring]) -> str:
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.title(_t='Bryan Family Playoff Pool')
            a.link(href='../css/csv_to_html.css', rel='stylesheet')
            a.link(href='../css/teams.css', rel='stylesheet')
            a.link(
                href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                rel='stylesheet',
                crossorigin='anonymous'
            )
            a.link(href='https://cdn.datatables.net/v/dt/dt-2.0.6/datatables.min.css', rel='stylesheet')
            a.script(src='https://code.jquery.com/jquery-3.7.1.min.js')
        with a.body():
            display_summary_table(a, all_rows)
            for i, rows in enumerate(all_rows):
                display_table(a, i+1, rows, nhl_api_handler, scoring[i])
    return str(a)


def display_summary_table(a: Airium, all_rows: list[list[Row]]):
    # if not all 4 rounds have happened yet, put in 0s
    while len(all_rows) < 4:
        rows = [
            Row(row.person, [], 0, 0)
            for row in all_rows[0]
        ]
        all_rows.append(rows)
    # arrange by person and calculate scores
    scores: dict[str, SummaryRow] = {}
    for round_rows in all_rows:
        for row in round_rows:
            summary_row = scores.get(row.person, SummaryRow(row.person, [], 0, 0))
            scores[row.person] = SummaryRow(
                row.person,
                summary_row.round_totals + [row.total_points],
                summary_row.total_points + row.total_points,
                summary_row.possible_points + row.possible_points
            )
    # render table
    with a.div(id='summary'):
        with a.table(klass='table table-striped containing_table table-hover', id='summaryTable'):
            with a.tr():
                a.th(_t='')
                a.th(_t='Round 1')
                a.th(_t='Round 2')
                a.th(_t='Round 3')
                a.th(_t='Round 4')
                a.th(_t='Total Points')
                a.th(_t='Rank')
                a.th(_t='Total Possible Points')
            # TODO: precalc rank
            all_points = list(map(lambda r: r.total_points, scores.values()))
            for summary_row in sorted(scores.values(), key=lambda s: (s.total_points, s.person), reverse=True):
                rank = excel_rank(all_points, summary_row.total_points)
                leader_class = ' leader' if rank == 1 and summary_row.total_points > 0 else ''
                with a.tr(klass=leader_class):
                    a.td(_t=summary_row.person, klass='person')
                    for round in summary_row.round_totals:
                        a.td(_t=to_str(round), klass='round_total')
                    a.td(_t=to_str(summary_row.total_points), klass='points')
                    a.td(_t=rank, klass='rank')
                    a.td(_t=to_str(summary_row.possible_points), klass='possible_points')


# hack necessary because airium considers 0 == None and doesnt display it
def to_str(num: int) -> str:
    return '0' if num == 0 else str(num)


def display_table(a: Airium, round: int, rows: list[Row], nhl_api_handler: NhlApiHandler, scoring: Scoring):
    round_str = f'round{round}'
    with a.div(id=round_str):
        a.h2(_t=f'Round {round}', href=f'#{round_str}')
        with a.ul():
            a.li(_t=f'Correct team: {scoring.team} point(s)')
            a.li(_t=f'Correct games: {scoring.games} point(s)')
            a.li(_t=f'Both correct: {scoring.bonus} bonus point(s)')
        with a.table(klass='table table-striped containing_table table-hover', id=f'{round_str}Table'):
            with a.tr():
                a.th(_t='')
                for series in nhl_api_handler.series_iter(round):
                    winning_seed_class = 'winning_seed'
                    top_seed_class = winning_seed_class if series.is_top_seed_winner() else ''
                    bottom_seed_class = winning_seed_class if series.is_bottom_seed_winner() else ''
                    with a.th():
                        a.span(_t=f'Series {series.letter}:')
                        a.br()
                        a.span(_t=series.get_top_seed_short(), klass=top_seed_class)
                        a.br()
                        a.span(_t=series.get_bottom_seed_short(), klass=bottom_seed_class)
                a.th(_t='Points')
                a.th(_t='Rank')
                a.th(_t='Possible Points')
            all_points = list(map(lambda r: r.total_points, rows))
            for row in sorted(rows, key=lambda x: x.person):
                rank = excel_rank(all_points, row.total_points)
                leader_class = ' leader' if rank == 1 and row.total_points > 0 else ''
                with a.tr():
                    a.td(_t=row.person, klass='person' + leader_class)
                    for result in sorted(row.pick_results, key=lambda r: r.series_letter):
                        with a.td():
                            with a.div(klass='pick'):
                                with a.div(klass=f'img_container {result.team_status.name.lower()}'):
                                    if result.pick:
                                        a.img(src=result.pick.team.logo, alt=result.pick.team.short)
                                a.div(_t=result.pick.games if result.pick else '', klass=f'games {result.games_status.name.lower()}')
                    a.td(_t=to_str(row.total_points), klass='points' + leader_class)
                    a.td(_t=rank, klass='rank' + leader_class)
                    a.td(_t=to_str(row.possible_points), klass='possible_points')


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
            csv_rows = read_csv(file_path)
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

    html = make_html(all_rows, nhl_api_handler, SCORING)
    out_path = os.path.join(folder_name, 'index.html')
    return html, out_path


if __name__ == '__main__':
    main(sys.argv[1])
