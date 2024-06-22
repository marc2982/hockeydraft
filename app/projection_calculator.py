from collections import defaultdict
from dataclasses import dataclass

from .common import Row, Team, Scoring, Pick


@dataclass
class ProjectionCell:
    winners: list[str]
    losers: list[str]
    is_possible: bool

    def short_desc(self):
        return f"winners: {self.winners}\nlosers: {self.losers}"


class ProjectionCalculator:
    def __init__(self, all_rows: list[list[Row]], all_picks: list[dict[str, Pick]], year: int):
        self.all_picks = all_picks
        self.all_rows = all_rows
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

                max_points = max(points.values())
                winners = [person for person, score in points.items() if score == max_points]
                min_points = min(points.values())
                losers = [person for person, score in points.items() if score == min_points]

                is_possible = True  # TODO
                cells[team] = ProjectionCell(winners, losers, is_possible)
            projections[games] = cells
        return projections

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
