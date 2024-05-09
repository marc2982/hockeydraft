from dataclasses import dataclass

from common import Team, Winner

ALL_SERIES = [
    ["A", "B", "C", "D", "E", "F", "G", "H"],
    ["I", "J", "K", "L"],
    ["M", "N"],
    ["O"],
]

WINNER_MAP = {
    'I': ['A', 'B'],
    'J': ['C', 'D'],
    'K': ['E', 'F'],
    'L': ['G', 'H'],
    'M': ['I', 'J'],
    'N': ['K', 'L'],
    'O': ['M', 'N']
}


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
        return self.top_seed and self.top_seed_wins == 4

    def is_bottom_seed_winner(self):
        return self.bottom_seed and self.bottom_seed_wins == 4

    def total_games(self):
        return self.top_seed_wins + self.bottom_seed_wins

    def get_winner(self):
        if self.is_top_seed_winner():
            return Winner(self.top_seed, self.total_games())
        if self.is_bottom_seed_winner():
            return Winner(self.bottom_seed, self.total_games())
        return None

    def get_top_seed_short(self) -> str:
        return (
            f"{self.top_seed.short} {self.top_seed_wins}"
            if self.top_seed else
            f"Winner {WINNER_MAP[self.letter][0]}"
        )

    def get_bottom_seed_short(self) -> str:
        return (
            f"{self.bottom_seed.short} {self.bottom_seed_wins}"
            if self.bottom_seed else
            f"Winner {WINNER_MAP[self.letter][1]}"
        )

    def get_series_summary(self) -> str:
        return f"{self.get_top_seed_short()} - {self.get_bottom_seed_short()}"
