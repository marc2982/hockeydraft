from collections import defaultdict
from dataclasses import dataclass

from .common import Row, Team, Scoring, Pick, excel_rank
from .nhl_api_handler import NhlApiHandler


@dataclass
class ProjectionCell:
    first: list[str]
    second: list[str]
    third: list[str]
    losers: list[str]
    is_possible: bool

    def short_desc(self):
        return f"winners: {self.winners}\nlosers: {self.losers}"


class ProjectionCalculator:
    def __init__(
        self,
        all_rows: list[list[Row]],
        all_picks: list[dict[str, Pick]],
        nhl_api_handler: NhlApiHandler,
        year: int
    ):
        self.all_picks = all_picks
        self.all_rows = all_rows
        self.api = nhl_api_handler
        self.year = year

    def calculate(
        self,
        scoring: list[Scoring],
        scf_teams: list[Team]
    ) -> dict[int, dict[str, ProjectionCell]]:
        if len(scf_teams) != 2 or len(self.all_picks) != 4:
            return self._create_empty_table()

        third_round_points = self._calculate_third_round_points()
        round_four_picks = self.all_picks[-1]
        round_four_scoring = scoring[-1]

        projections: dict[int, dict[str, ProjectionCell]] = {}
        for games in range(4, 8):
            cells: map[str, ProjectionCell] = {}
            for team in scf_teams:
                points: dict[str, int] = third_round_points.copy()
                for person in points.keys():
                    points[person] += self._calculate_fourth_round(
                        round_four_scoring,
                        round_four_picks[person][0],
                        team,
                        games
                    )

                all_points = points.values()
                rank_map = {person: excel_rank(all_points, score) for person, score in points.items()}
                loser_rank = max(rank_map.values())

                cells[team] = ProjectionCell(
                    first=[f"{person} ({points[person]} pts)" for person, rank in rank_map.items() if rank == 1],
                    second=[f"{person} ({points[person]} pts)" for person, rank in rank_map.items() if rank == 2],
                    third=[f"{person} ({points[person]} pts)" for person, rank in rank_map.items() if rank == 3],
                    losers=[f"{person} ({points[person]} pts)" for person, rank in rank_map.items() if rank == loser_rank],
                    is_possible=self._calculate_is_possible(team, games)
                )
            projections[games] = cells
        return projections

    def _calculate_is_possible(self, team, games) -> bool:
        scf_series = self.api.get_scf_series()

        if scf_series.is_over():
            if scf_series.is_top_seed_winner():
                return team == scf_series.top_seed and games == scf_series.top_seed_wins
            return team == scf_series.bottom_seed and games == scf_series.bottom_seed_wins

        top_seed = (scf_series.top_seed, scf_series.top_seed_wins)
        bottom_seed = (scf_series.bottom_seed, scf_series.bottom_seed_wins)
        if top_seed[0] == team:
            seed = top_seed
            other_seed = bottom_seed
        else:
            other_seed = top_seed
            seed = bottom_seed
        min_games_to_win = (4 - seed[1]) + seed[1] + other_seed[1]
        return games >= min_games_to_win

    def _calculate_third_round_points(self) -> defaultdict[str, int]:
        points = defaultdict(int)
        for round_rows in self.all_rows:
            for row in round_rows:
                points[row.person] += row.total_points
        return points

    def _calculate_fourth_round(self, scoring: Scoring, pick: Pick, team: str, games: int) -> int:
        team_points = scoring.team if pick.team == team else 0
        game_points = scoring.games if pick.games == games else 0
        bonus_points = scoring.bonus if team_points > 0 and game_points > 0 else 0
        return team_points + game_points + bonus_points

    def _create_empty_table(self) -> list[list[ProjectionCell]]:
        return [
            ProjectionCell(
                winners="-",
                losers="-",
                is_possible=None
            )
            for _ in range(4, 8)  # games 4 -> 7
            for _ in range(2)  # 2 teams left
        ]
