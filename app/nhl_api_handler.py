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
        print(f"Calling API: {self.url}")
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

            if series["seriesTitle"] == "Stanley Cup Final":
                break

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

        if "logo" not in seed: print(seed)
        team = Team(
            name=seed["name"]["default"],
            short=short,
            logo=seed["logo"],
            rank=series[f"{top_or_bottom}SeedRankAbbrev"],
            is_top_seed=True if top_or_bottom == TOP else False
        )

        self.teams[team.short] = team
        return team

    # team_pick_str matches the full name of the team in picks.csv
    def get_team(self, team_pick_str: str) -> Team:
        # handle team discrepancies between picks and api
        # also handle older years when picks were only shorthand
        conversion_map = {
            "CAL": "CGY",
            "CLB": "CBJ",
            "LA": "LAK",
            "LV": "VGK",
            "MON": "MTL",
            "Montreal Canadiens": "Montréal Canadiens",
            "NAS": "NSH",
            "NASH": "NSH",
            "NJ": "NJD",
            "PHE": "PHX",
            "PHO": "PHX",
            "SJ": "SJS",
            "St Louis Blues": "St. Louis Blues",
            "TB": "TBL",
            "WAS": "WSH",
        }
        team_pick_str = conversion_map.get(team_pick_str, team_pick_str)

        try:
            return next(  # return first occurrence or die
                team
                for team in self.teams.values()
                if team_pick_str in [team.name, team.short]
            )
        except StopIteration:
            raise Exception(f"Could not find {team_pick_str}")

    def get_series(self, letter: str) -> Series:
        return next(  # return first occurrence or die
            series
            for series in self.series
            if series.letter == letter
        )

    def series_iter(self, round: int) -> Generator[str, any, any]:
        order = ALL_SERIES[round-1]
        for letter in order:
            yield self.get_series(letter)
