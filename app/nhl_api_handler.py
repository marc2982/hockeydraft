from typing import Generator
import requests

from .common import Team
from .series import Series, ALL_SERIES

NHL_API_URL = "https://api-web.nhle.com/v1/playoff-bracket/{0:d}"  # TODO
TOP = "top"
BOTTOM = "bottom"


class NhlApiHandler:
    def __init__(self, year: int):
        self.year = year
        self.url = NHL_API_URL.format(year)
        self.teams: dict[str, Team] = {}
        self.series: list[Series] = []

    def load(self):
        response = requests.get(self.url)
        response.raise_for_status()

        for series in response.json()["series"]:
            if "seriesUrl" not in series:
                continue  # series not fully set yet

            top_seed = self._build_team(series, TOP)
            bottom_seed = self._build_team(series, BOTTOM)

            self.series.append(Series(
                letter=series["seriesLetter"],
                round=series["playoffRound"],
                top_seed=top_seed,
                bottom_seed=bottom_seed,
                top_seed_wins=series["topSeedWins"],
                bottom_seed_wins=series["bottomSeedWins"]
            ))

        # add future series to the list
        existing_letters = map(lambda s: s.letter, self.series)
        for i, round in enumerate(ALL_SERIES):
            for series_letter in round:
                if series_letter in existing_letters:
                    continue  # already have a record of it
                self.series.append(Series(
                    letter=series_letter,
                    round=i+1,
                    top_seed=None,
                    bottom_seed=None,
                    top_seed_wins=0,
                    bottom_seed_wins=0
                ))

    def _build_team(self, series: dict, top_or_bottom: str) -> Team:
        seed = series[f"{top_or_bottom}SeedTeam"]
        short = seed["abbrev"]

        # only need to load each team once
        if short in self.teams:
            return self.teams[short]

        team = Team(
            name=seed["name"]["default"],
            short=short,
            logo=seed["logo"],
            rank=self._convert_rank(series[f"{top_or_bottom}SeedRankAbbrev"], short),
            is_top_seed=True if top_or_bottom == TOP else False
        )

        self.teams[team.short] = team
        return team

    # !!!2024 hack only!!!
    # we used A, C, M, P to indicate division, but the api only uses D (for division)
    # in the future we should use D to be consistent, but for this year (2024) we have to convert
    def _convert_rank(self, rank: str, short: str) -> str:
        if self.year != 2024:
            return rank
        if rank[0] == "D":
            if short in ["VAN", "EDM", "LAK"]:  # pacific
                return f"P{rank[1]}"
            if short in ["FLA", "TOR", "BOS"]:  # atlantic
                return f"A{rank[1]}"
            if short in ["CAR", "NYI", "NYR"]:  # metropolitan
                return f"M{rank[1]}"
            if short in ["DAL", "COL", "WPG"]:  # central
                return f"C{rank[1]}"
        return rank

    # team_pick_str matches the full name of the team in picks.csv
    def get_team(self, team_pick_str: str) -> Team:
        return next(  # return first occurrence or die
            team
            for team in self.teams.values()
            if f"{team.name} ({team.rank})" == team_pick_str
            or team.name == team_pick_str
        )

    def get_series(self, letter: str) -> Series:
        return next(  # return first occurrence or die
            series
            for series in self.series
            if series.letter == letter
        )

    def _get_series_order(self, round: int) -> list[str]:
        if round == 1 and self.year == 2024:
            # !!!2024 hack only!!!
            # since the form doesnt follow the letter order that the api does,
            # hardcode the order of the first round of 2024
            return ["G", "H", "A", "B", "C", "D", "E", "F"]
        return ALL_SERIES[round - 1]

    def series_iter(self, round: int) -> Generator[str, any, any]:
        order = self._get_series_order(round)
        for letter in order:
            yield self.get_series(letter)
