from airium import Airium

from .common import Row, Scoring, SummaryRow
from .leader_calculator import LeaderCalculator
from .nhl_api_handler import NhlApiHandler

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


class HtmlGenerator:
    def __init__(
        self,
        nhl_api_handler: NhlApiHandler,
        all_rows: list[list[Row]],
    ) -> None:
        self.api = nhl_api_handler
        self.all_rows = all_rows

        self.summary_map = self._generate_summary_rows()
        self.rank_map = self.calculate_rank_map(self.summary_map)
        self.leaders = LeaderCalculator().calculate(all_rows, self.summary_map, self.rank_map)
        self.a = Airium()

    def make_html(
        self,
        scoring: list[Scoring],
        year: int
    ) -> str:
        self.a('<!DOCTYPE html>')
        with self.a.html(lang='en'):
            with self.a.head():
                self.a.title(_t=f'{year} Bryan Family Playoff Pool')
                self.a.link(href='../css/csv_to_html.css', rel='stylesheet')
                self.a.link(href='../css/teams.css', rel='stylesheet')

                self.a.script(src='https://code.jquery.com/jquery-3.7.1.min.js')
                self.a.script(src="https://cdn.datatables.net/2.0.8/js/dataTables.js")

                self.a.link(
                    href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
                    rel='stylesheet'
                )
                self.a.link(href='https://cdn.datatables.net/v/dt/dt-2.0.8/datatables.min.css', rel='stylesheet')
                self.a.script(_t=js)
            with self.a.body():
                with self.a.div(id='backToIndex'):
                    with self.a.a(href="index.html"):
                        self.a.strong(_t="← Back to all years")
                with self.a.div():
                    self.a.h1(_t=year, klass='text-center bg-secondary', style="--bs-bg-opacity: .2;")
                self._display_tiebreaker()
                if not self.leaders.winner:
                    self.a.h2(_t="Tiebreak needs to be decided manually!", style="color: red")
                self._display_summary_table()
                for i, rows in enumerate(self.all_rows):
                    self._display_round(i+1, rows, scoring[i])
        return str(self.a)

    def _generate_summary_rows(self) -> dict[str, SummaryRow]:
        # if not all 4 rounds have happened yet, put in 0s
        while len(self.all_rows) < 4:
            rows = [
                Row(row.person, [], 0, 0)
                for row in self.all_rows[0]
            ]
            self.all_rows.append(rows)
        # arrange by person and calculate scores
        scores: dict[str, SummaryRow] = {}
        for round_rows in self.all_rows:
            for row in round_rows:
                summary_row = scores.get(row.person, SummaryRow(row.person, [], 0, 0))
                scores[row.person] = SummaryRow(
                    row.person,
                    summary_row.round_totals + [row.total_points],
                    summary_row.total_points + row.total_points,
                    summary_row.possible_points + row.possible_points
                )
        return scores

    def _display_tiebreaker(self):
        if len(self.leaders.leaders) > 1:
            with self.a.div(id="tiebreaker"):
                self.a.h2(_t="Tiebreaker!")
                with self.a.ol():
                    self.a.li(_t='Number of games correct')
                    self.a.li(_t='Number of teams correct')
                    self.a.li(_t='Number of goals scored in the final series, ideally chosen before it begins')
                    self.a.li(_t='Coin flip')
                with self.a.table(klass='table table-striped containing_table table-hover', id='tiebreakerTable'):
                    with self.a.thead():
                        with self.a.tr():
                            self.a.th(_t="Name")
                            self.a.th(_t="# of correct games")
                            self.a.th(_t="# of correct teams")
                    with self.a.tbody():
                        for leader in self.leaders.leaders:
                            leader_class = " leader" if leader == self.leaders.winner else ""
                            with self.a.tr(klass=leader_class):
                                self.a.td(_t=leader, klass='person' + leader_class)
                                self.a.td(_t=self.leaders.games_map[leader])
                                self.a.td(_t=self.leaders.teams_map[leader])
        return self.leaders.winner

    def _display_summary_table(self):
        with self.a.div(id='summary'):
            self.a.h2(_t='Overall', href='overall')
            with self.a.table(klass='table table-striped containing_table table-hover', id='summaryTable'):
                with self.a.tr():
                    self.a.th(_t='')
                    self.a.th(_t='Round 1')
                    self.a.th(_t='Round 2')
                    self.a.th(_t='Round 3')
                    self.a.th(_t='Round 4')
                    self.a.th(_t='Total Points')
                    self.a.th(_t='Rank')
                    self.a.th(_t='Maximum Possible Points')
                sorted_summaries = sorted(
                    self.summary_map.values(),
                    key=lambda s: (s.total_points, s.person),
                    reverse=True
                )
                for summary_row in sorted_summaries:
                    leader_class = ' leader' if self.rank_map[summary_row.person] == 1 else ''
                    with self.a.tr(klass=leader_class):
                        self.a.td(_t=summary_row.person, klass='person')
                        for round in summary_row.round_totals:
                            self.a.td(_t=self.to_str(round), klass='round_total')
                        self.a.td(_t=self.to_str(summary_row.total_points), klass='points')
                        self.a.td(_t=self.rank_map[summary_row.person], klass='rank')
                        self.a.td(_t=self.to_str(summary_row.possible_points), klass='possible_points')

    def _display_round(
        self,
        round: int,
        rows: list[Row],
        scoring: Scoring
    ):
        round_str = f'round{round}'
        with self.a.div(id=round_str):
            self.a.h2(_t=f'Round {round}', href=f'#{round_str}')
            with self.a.ul():
                self.a.li(_t=f'Correct team: {scoring.team} point(s)')
                self.a.li(_t=f'Correct games: {scoring.games} point(s)')
                self.a.li(_t=f'Both correct: {scoring.bonus} bonus point(s)')
            with self.a.table(klass='table table-striped containing_table table-hover', id=f'{round_str}Table'):
                with self.a.tr():
                    self.a.th(_t='')
                    for series in self.api.series_iter(round):
                        winning_seed_class = 'winning_seed'
                        top_seed_class = winning_seed_class if series.is_top_seed_winner() else ''
                        bottom_seed_class = winning_seed_class if series.is_bottom_seed_winner() else ''
                        with self.a.th():
                            self.a.span(_t=f'Series {series.letter}:')
                            self.a.br()
                            self.a.span(_t=series.get_top_seed_short(), klass=top_seed_class)
                            self.a.br()
                            self.a.span(_t=series.get_bottom_seed_short(), klass=bottom_seed_class)
                    self.a.th(_t='Points')
                    self.a.th(_t='Rank')
                    self.a.th(_t='Maximum Possible Points')
                all_points = list(map(lambda r: r.total_points, rows))
                for row in sorted(rows, key=lambda x: x.person):
                    rank = self.excel_rank(all_points, row.total_points)
                    leader_class = ' leader' if rank == 1 and row.total_points > 0 else ''
                    with self.a.tr():
                        self.a.td(_t=row.person, klass='person' + leader_class)
                        for result in sorted(row.pick_results, key=lambda r: r.series_letter):
                            with self.a.td():
                                with self.a.div(klass='pick'):
                                    with self.a.div(klass=f'img_container {result.team_status.name.lower()}'):
                                        if result.pick:
                                            self.a.img(src=result.pick.team.logo, alt=result.pick.team.short)
                                    self.a.div(
                                        _t=result.pick.games if result.pick else '',
                                        klass=f'games {result.games_status.name.lower()}'
                                    )
                        self.a.td(_t=self.to_str(row.total_points), klass='points' + leader_class)
                        self.a.td(_t=rank, klass='rank' + leader_class)
                        self.a.td(_t=self.to_str(row.possible_points), klass='possible_points')

    @staticmethod
    # hack necessary because airium considers 0 == None and doesnt display it
    def to_str(num: int) -> str:
        return '0' if num == 0 else str(num)

    @staticmethod
    def calculate_rank_map(scores: dict[str, SummaryRow]) -> dict[str, int]:
        summary_rows = scores.values()
        all_points = list(map(lambda r: r.total_points, summary_rows))
        return {
            summary_row.person: HtmlGenerator.excel_rank(all_points, summary_row.total_points)
            for summary_row in summary_rows
        }

    @staticmethod
    def excel_rank(values, target):
        sorted_values = sorted(values, reverse=True)
        try:
            return sorted_values.index(target) + 1
        except ValueError:
            return None
