from collections import defaultdict, namedtuple

from .common import PickStatus, Row, SummaryRow

Leaders = namedtuple("Leaders", "leaders teams_map games_map winner")


class LeaderCalculator:
    def calculate(
        self,
        all_rows: list[list[Row]],
        summary_map: dict[str, SummaryRow],
        rank_map: dict[str, int]
    ) -> Leaders:
        leaders = self._get_current_leaders(summary_map, rank_map)
        leaders_obj = Leaders(leaders, {}, {}, None)

        if len(leaders) == 1:
            return leaders_obj._replace(winner=leaders[0])

        num_teams_correct, num_games_correct = self._calculate_tiebreaker_data(all_rows, leaders)
        leaders_obj = leaders_obj._replace(teams_map=num_teams_correct, games_map=num_games_correct)

        # first compare who got the most games correct
        new_leaders = self._tiebreak(num_games_correct, leaders)
        if len(new_leaders) == 1:
            return leaders_obj._replace(winner=new_leaders[0])

        # next compare who got the most teams correct
        new_leaders = self._tiebreak(num_teams_correct, new_leaders)
        if len(new_leaders) == 1:
            return leaders_obj._replace(winner=new_leaders[0])

        return leaders_obj

    def _get_current_leaders(
        self,
        scores: dict[str, SummaryRow],
        rank_map: dict[dict, int]
    ) -> list[str]:
        leaders = [person for (person, rank) in rank_map.items() if rank == 1]
        if len(leaders) < 1:
            raise Exception(f"something went wrong {rank_map}")
        return [person for person in leaders if scores[person].total_points > 0]

    def _calculate_tiebreaker_data(
        self,
        all_rows: list[list[Row]],
        leaders: list[str]
    ) -> tuple[dict[str, int], dict[str, int]]:
        # tiebreaker time
        num_teams_correct = defaultdict(int)
        num_games_correct = defaultdict(int)
        for round_rows in all_rows:
            for row in round_rows:
                if row.person not in leaders:
                    continue
                for result in row.pick_results:
                    if result.team_status == PickStatus.CORRECT:
                        num_teams_correct[row.person] += 1
                    if result.games_status == PickStatus.CORRECT:
                        num_games_correct[row.person] += 1
        return num_teams_correct, num_games_correct

    def _tiebreak(
        self,
        data: dict[str, int],
        leaders: list[str]
    ) -> list[str]:
        if not data:
            return leaders
        max_correct = max(data.values())
        new_leaders = [
            person
            for person in leaders
            if data[person] == max_correct
        ]
        if len(new_leaders) < 1:
            raise Exception(f"something went wrong {max_correct} {data}")
        return new_leaders
