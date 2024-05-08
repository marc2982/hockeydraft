from collections import namedtuple
from dataclasses import dataclass

PickResult = namedtuple("PickResult", "pick points possible_points team_status games_status")
Row = namedtuple("Row", "person pick_results total_points possible_points")
Scoring = namedtuple("Scoring", "team games bonus")
SummaryRow = namedtuple("SummaryRow", "person round_totals total_points possible_points")
Team = namedtuple("Team", "name short logo rank is_top_seed")
Winner = namedtuple("Winner", "team games")


@dataclass
class Pick:
    series_letter: str
    team: Team
    games: int

    def get_short_desc(self):
        return f"{self.team.short} {self.games}"


@dataclass
class Series:
    letter: str
    round: int
    top_seed: Team
    bottom_seed: Team
    top_seed_wins: int
    bottom_seed_wins: int

    def get_short_desc(self):
        return f"{self.top_seed.short} vs {self.bottom_seed.short}"

    def is_over(self):
        return self.is_top_seed_winner() or self.is_bottom_seed_winner()

    def is_top_seed_winner(self):
        return self.top_seed_wins == 4

    def is_bottom_seed_winner(self):
        return self.bottom_seed_wins == 4

    def total_games(self):
        return self.top_seed_wins + self.bottom_seed_wins

    def get_winner(self):
        if self.is_top_seed_winner():
            return Winner(self.top_seed, self.total_games())
        if self.is_bottom_seed_winner():
            return Winner(self.bottom_seed, self.total_games())
        return None

    def get_top_seed_short(self) -> str:
        return f"{self.top_seed.short} {self.top_seed_wins}"

    def get_bottom_seed_short(self) -> str:
        return f"{self.bottom_seed.short} {self.bottom_seed_wins}"

    def get_series_summary(self) -> str:
        return f"{self.get_top_seed_short()} - {self.get_bottom_seed_short()}"
