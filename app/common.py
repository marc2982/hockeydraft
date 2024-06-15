from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

PickResult = namedtuple("PickResult", "series_letter pick points possible_points team_status games_status")
Row = namedtuple("Row", "person pick_results total_points possible_points")
Scoring = namedtuple("Scoring", "team games bonus")
SummaryRow = namedtuple("SummaryRow", "person round_totals total_points possible_points")
Team = namedtuple("Team", "name short logo rank is_top_seed")
Winner = namedtuple("Winner", "team games")


PickStatus = Enum('PickStatus', [
    'CORRECT',
    'INCORRECT',
    'UNKNOWN'
])


@dataclass
class Pick:
    series_letter: str
    team: Team
    games: int

    def get_short_desc(self):
        return f"{self.team.short} {self.games}"
