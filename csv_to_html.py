#!/usr/bin/env python3
import csv
import sys
from collections import namedtuple


Team = namedtuple("Team", "short colour img")
Pick = namedtuple("Pick", "team games")
Winner = namedtuple("Winner", "team games")
Scoring = namedtuple("Scoring", "team games bonus")

SCORING = [
    Scoring(1, 2, 3),
    Scoring(2, 3, 4),
    Scoring(3, 4, 5),
    Scoring(4, 5, 6)
]

DATA = {
    "Boston Bruins (A2)": Team("BOS", "000000", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/6.svg"),
    "Carolina Hurricanes (M2)": Team("CAR", "CE1126", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/12.svg"),
    "Colorado Avalanche (C3)": Team("COL", "6F263D", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/21.svg"),
    "Dallas Stars (C1)": Team("DAL", "006847", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/25.svg"),
    "Edmonton Oilers (P2)": Team("EDM", "FF4C00", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/22.svg"),
    "Florida Panthers (A1)": Team("FLA", "C8102E", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/13.svg"),
    "Los Angeles Kings (P3)": Team("LAK", "111111", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/26.svg"),
    "Nashville Predators (WC1)": Team("NAS", "FFB81C", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/18.svg"),
    "New York Islanders (M3)": Team("NYI", "F47D30", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/2.svg"),
    "New York Rangers (M1)": Team("NYR", "0038A8", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/3.svg"),
    "Tampa Bay Lightning (WC1)": Team("TBL", "002469", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/14.svg"),
    "Toronto Maple Leafs (A3)": Team("TOR", "00205B", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/10.svg"),
    "Vancouver Canucks (P1)": Team("VAN", "00843D", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/23.svg"),
    "Vegas Golden Knights (WC2)": Team("VGK", "B4975A", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/54.svg"),
    "Washington Capitals (WC2)": Team("WAS", "C8102E", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/15.svg"),
    "Winnipeg Jets (C2)": Team("WSH", "55565A", "https://allstarvotefilesde.blob.core.windows.net/nhl-team-logos/52.svg")
}

WINNERS = [
    None,
    None,
    Winner("FLA", 5),
    None,
    Winner("NYR", 4),
    Winner("CAR", 5),
    None,
    Winner("COL", 5)
]


def read_csv(csv_filename):
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the headers
        return [row for row in reader]


def read_picks_round1(rows):
    trs = {}
    for row in rows:
        tds = []
        person = row[1]
        col_iter = iter(row[2:])

        for col in col_iter:
            team_name = col
            num_games = next(col_iter)

            pick = Pick(
                team=DATA[team_name],
                games=int(num_games)
            )

            tds.append(pick)
        trs[person] = tds
    return trs


def make_html(trs):
    s = ["<html>\n"]
    s.append("<head>")
    s.append("<link rel=\"stylesheet\" type=\"text/css\" href=\"csv_to_html.css\"/>")
    s.append("</head>")
    s.append("<body>\n")

    s.append("<div width=500px style=\"background-color: light-gray;\">\n")
    s.append("<table style=\"padding: 5px\">\n")

    sorted_persons = sorted(trs.keys())
    for person in sorted_persons:
        points = 0
        possible_points = 0
        picks = trs[person]
        s.append("<tr>")
        s.append(f"<td><b>{person}</b></td>")

        for (i, pick) in enumerate(picks):
            winner = WINNERS[i]
            scoring = SCORING[0]  # TODO
            points += get_points(scoring, pick, winner)
            possible_points += calculate_possible_points(scoring, pick, winner)
            team_class = get_team_class(pick, winner)
            games_class = get_games_class(pick, winner)

            s.append(f"<td style=\"color: #FFFFFF; font-weight: bold; background-color: #{pick.team.colour};\">")
            s.append("<table class=\"pick\">")
            s.append("<tr>")
            s.append(f"<td><img src=\"{pick.team.img}\" height=50 width=50></img></td>")
            s.append(f"<td><span class=\"{team_class}\"></span></td>")
            s.append("</tr>")
            s.append("<tr>")
            s.append(f"<td>{pick.games}</td>")
            s.append(f"<td><span class=\"{games_class}\"></span></td>")
            s.append("</tr>")
            s.append("</table>")
            s.append("</td>")

        s.append(f"<td><b>{points}</b></td>")
        s.append(f"<td><b>{possible_points}</b></td>")
        s.append("</tr>\n")

    s.append("</table></div>")
    s.append("</body>")
    s.append("</html>")
    return s


def get_team_class(pick: Pick, winner: Winner):
    if not winner:
        return ""
    if pick.team.short == winner.team:
        return "correct"
    return "incorrect"


def get_games_class(pick: Pick, winner: Winner):
    if not winner:
        return ""
    if pick.games == winner.games:
        return "correct"
    return "incorrect"


def get_points(scoring: Scoring, pick: Pick, winner: Winner) -> int:
    if not winner:
        return 0
    points = 0
    points += scoring.team if pick.team.short == winner.team else 0
    points += scoring.games if pick.games == winner.games else 0
    points += scoring.bonus if points == scoring.team + scoring.games else 0
    return points


def calculate_possible_points(scoring: Scoring, pick: Pick, winner: Winner) -> int:
    if not winner:
        return scoring.team + scoring.games + scoring.bonus
    return get_points(scoring, pick, winner)


def write_html(html, filename):
    with open(filename, 'w') as f:
        for row in html:
            f.write(row)


def main(argv):
    rows = read_csv(argv[1])
    trs = read_picks_round1(rows)
    html = make_html(trs)
    write_html(html, "round1.html")


if __name__ == "__main__":
    main(sys.argv)

