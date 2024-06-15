#!/usr/bin/env python3
import csv
import os
import sys

from airium import Airium

from .common import Scoring, Winner, Pick, PickResult, PickStatus, Row, SummaryRow
from .leader_calculator import LeaderCalculator
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


js = """
window.onload = function() {
    $('#tiebreakerTable').DataTable({
        paging: false,
        searching: false,
        info: false,
        order: [
            [1, 'desc'],
            [2, 'desc'],
        ],
        columnDefs: [
            { targets: [0,1,2], className: 'dt-body-center dt-head-center' }
        ]
    });
}
"""


def make_html(
    all_rows: list[list[Row]],
    nhl_api_handler: NhlApiHandler,
    scoring: list[Scoring],
    year: int
) -> str:
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.title(_t=f'{year} Bryan Family Playoff Pool')
            a.link(href='../css/csv_to_html.css', rel='stylesheet')
            a.link(href='../css/teams.css', rel='stylesheet')

            a.script(src='https://code.jquery.com/jquery-3.7.1.min.js')
            a.script(src="https://cdn.datatables.net/2.0.8/js/dataTables.js")

            a.link(
                href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                rel='stylesheet'
            )
            a.link(href='https://cdn.datatables.net/v/dt/dt-2.0.8/datatables.min.css', rel='stylesheet')
            a.script(_t=js)
        with a.body():
            with a.div(id='backToIndex'):
                with a.a(href="index.html"):
                    a.strong(_t="← Back to all years")
            with a.div():
                a.h1(_t=year, klass='text-center bg-secondary', style="--bs-bg-opacity: .2;")
            summary_map = generate_summary_rows(all_rows)
            rank_map = calculate_rank_map(summary_map)
            leader = display_tiebreaker(a, all_rows, summary_map, rank_map)
            if not leader:
                a.h2(_t="Tiebreak needs to be decided manually!", style="color: red")
            display_summary_table(a, summary_map, rank_map)
            for i, rows in enumerate(all_rows):
                display_table(a, i+1, rows, nhl_api_handler, scoring[i])
    return str(a)


def display_tiebreaker(
    a: Airium,
    all_rows: list[list[Row]],
    summary_map: dict[str, SummaryRow],
    rank_map: dict[str, int]
) -> str:
    leaders = LeaderCalculator().calculate(all_rows, summary_map, rank_map)
    if len(leaders.leaders) > 1:
        with a.div(id="tiebreaker"):
            a.h2(_t="Tiebreaker!")
            with a.ol():
                a.li(_t='Number of teams correct')
                a.li(_t='Number of games correct')
                a.li(_t='Number of goals scored in the final series, ideally chosen before it begins')
                a.li(_t='Coin flip')
            with a.table(klass='table table-striped containing_table table-hover', id='tiebreakerTable'):
                with a.thead():
                    with a.tr():
                        a.th(_t="Name")
                        a.th(_t="# of correct teams")
                        a.th(_t="# of correct games")
                with a.tbody():
                    for leader in leaders.leaders:
                        leader_class = " leader" if leader == leaders.winner else ""
                        with a.tr(klass=leader_class):
                            a.td(_t=leader, klass='person' + leader_class)
                            a.td(_t=leaders.teams_map[leader])
                            a.td(_t=leaders.games_map[leader])
    return leaders.winner


def generate_summary_rows(all_rows: list[list[Row]]) -> dict[str, SummaryRow]:
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
    return scores


def display_summary_table(
    a: Airium,
    summary_rows: dict[str, SummaryRow],
    rank_map: dict[str, int]
):
    with a.div(id='summary'):
        a.h2(_t='Overall', href='overall')
        with a.table(klass='table table-striped containing_table table-hover', id='summaryTable'):
            with a.tr():
                a.th(_t='')
                a.th(_t='Round 1')
                a.th(_t='Round 2')
                a.th(_t='Round 3')
                a.th(_t='Round 4')
                a.th(_t='Total Points')
                a.th(_t='Rank')
                a.th(_t='Maximum Possible Points')
            for summary_row in sorted(summary_rows.values(), key=lambda s: (s.total_points, s.person), reverse=True):
                leader_class = ' leader' if rank_map[summary_row.person] == 1 else ''
                with a.tr(klass=leader_class):
                    a.td(_t=summary_row.person, klass='person')
                    for round in summary_row.round_totals:
                        a.td(_t=to_str(round), klass='round_total')
                    a.td(_t=to_str(summary_row.total_points), klass='points')
                    a.td(_t=rank_map[summary_row.person], klass='rank')
                    a.td(_t=to_str(summary_row.possible_points), klass='possible_points')


def calculate_rank_map(scores: dict[str, SummaryRow]) -> dict[str, int]:
    summary_rows = scores.values()
    all_points = list(map(lambda r: r.total_points, summary_rows))
    return {
        summary_row.person: excel_rank(all_points, summary_row.total_points)
        for summary_row in summary_rows
    }


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
                                a.div(
                                    _t=result.pick.games if result.pick else '',
                                    klass=f'games {result.games_status.name.lower()}'
                                )
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

    html = make_html(all_rows, nhl_api_handler, SCORING, year)
    out_path = os.path.join(folder_name, 'index.html')
    return html, out_path


if __name__ == '__main__':
    main(sys.argv[1])
