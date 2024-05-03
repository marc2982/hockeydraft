from collections import namedtuple
from dataclasses import dataclass

Pick = namedtuple("Pick", "series_letter team games")
PickResult = namedtuple("PickResult", "pick points possible_points team_status games_status")
Row = namedtuple("Row", "person pick_results")
Scoring = namedtuple("Scoring", "team games bonus")
Team = namedtuple("Team", "name short logo rank is_top_seed")
Winner = namedtuple("Winner", "team games")


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
        return self.top_seed_wins == 4 or self.bottom_seed_wins == 4

    def total_games(self):
        return self.top_seed_wins + self.bottom_seed_wins

    def get_winner(self):
        if self.top_seed_wins == 4:
            return Winner(self.top_seed, self.total_games())
        if self.bottom_seed_wins == 4:
            return Winner(self.bottom_seed, self.total_games())
        return None

    def get_series_summary(self):
        return f"{self.top_seed.short} {self.top_seed_wins} - {self.bottom_seed.short} {self.bottom_seed_wins}"
