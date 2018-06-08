
import random, math
from standings import init
from constants import *
from outcomes import *
from matches import matches

def get_random_float_between(lower_bound, upper_bound):
    return random.uniform(lower_bound, upper_bound)

def get_match_expectation(rating_a, rating_b):
    exponent = (rating_b - rating_a)/400.0
    return 1/(1 + (10**exponent))

def get_outcome_probabilities(a_elo, b_elo):
    exp = get_match_expectation(a_elo, b_elo)
    k = 4.0/3.0
    pr_draw = (k * exp) * (1 - exp)
    pr_a_win = exp - (0.5 * pr_draw)
    pr_a_loss = 1 - pr_draw - pr_a_win
    return pr_a_loss, pr_draw

def get_match_score(result):
    result_key = str(result)
    possible_scores = OUTCOMES[result_key]
    return random.choice(possible_scores)

def get_match_outcome(a_elo, b_elo):
    pr_a_loss, pr_a_draw = get_outcome_probabilities(a_elo, b_elo)
    outcome_float = get_random_float_between(0, 1)
    if outcome_float < pr_a_loss:
        return LOSS
    elif outcome_float < pr_a_loss + pr_a_draw:
        return DRAW
    else:
        return WIN

def get_updated_elo(prev, exp, outcome):
    WORLD_CUP_CONSTANT = 60
    new_rating = prev + (WORLD_CUP_CONSTANT * (outcome - exp))
    return new_rating

def update_points(match_data, teams):
    team_a = match_data["a"]["name"]
    a_i = match_data["a"]["index"]
    team_b = match_data["b"]["name"]
    b_i = match_data["b"]["index"]
    outcome = match_data["outcome"]

    if (outcome == WIN):
        teams[a_i][PTS] += 3
    elif (outcome == DRAW):
        teams[a_i][PTS] += 1
        teams[b_i][PTS] += 1
    else:
        teams[b_i][PTS] += 3

    return teams

def update_standings(match_data, teams):
    team_a = match_data["a"]["name"]
    prev_a_elo = match_data["a"][ELO]
    a_i = match_data["a"]["index"]
    team_b = match_data["b"]["name"]
    prev_b_elo = match_data["b"][ELO]
    b_i = match_data["b"]["index"]
    exp = match_data["exp"]
    outcome = match_data["outcome"]
    new_a_elo = get_updated_elo(prev_a_elo, exp, outcome)
    new_b_elo = get_updated_elo(prev_b_elo, 1 - exp, abs(1 - outcome))
    teams[a_i][ELO] = int(round(new_a_elo))
    teams[b_i][ELO] = int(round(new_b_elo))

    return teams

def update_team_goals(match_data, teams):
    team_a = match_data["a"]["name"]
    a_goals = match_data["a"]["scored"]
    a_i = match_data["a"]["index"]
    team_b = match_data["b"]["name"]
    b_goals = match_data["b"]["scored"]
    b_i = match_data["b"]["index"]

    teams[a_i][GF] += a_goals
    teams[a_i][GA] += b_goals
    teams[b_i][GF] += b_goals
    teams[b_i][GA] += a_goals
    return teams

def sim_match(a_name, b_name, teams):
    a_team = [x for x in teams if x["name"] == a_name][0]
    b_team = [x for x in teams if x["name"] == b_name][0]

    a_index = -1
    b_index = -1

    for i in range(len(teams)):
        if teams[i]["name"] == a_name:
            a_index = i
        if teams[i]["name"] == b_name:
            b_index = i 

    a_elo = a_team[ELO]
    b_elo = b_team[ELO]
    outcome = get_match_outcome(a_elo, b_elo)
    exp = get_match_expectation(a_elo, b_elo)
    a_goals, b_goals = get_match_score(outcome)
    match_data = {"a": {"name": a_name, "scored": a_goals, "elo": a_elo, "index": a_index},
                "b": {"name": b_name, "scored": b_goals, "elo": b_elo, "index": b_index},
                "exp": exp,
                "outcome": outcome}
    teams = update_team_goals(match_data, teams)
    teams = update_points(match_data, teams)
    teams = update_standings(match_data, teams)
    return teams

def print_group(standings, group_name):
    group = [x for x in standings if x["group"] == group_name]
    sorted_group = sorted(group, key=lambda k: k["points"])[::-1]
    for team in sorted_group:
        print(team)

def pretty_print(standings):
    groups = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for group in groups:
        print_group(standings, group)
        print("")

def sim_group_stage():
    standings = init()
    for match in matches:
        a_name = match["home"]
        b_name = match["away"]
        standings = sim_match(a_name, b_name, standings)
    return standings

def get_top_two_from(curr_standings, group_name):
    group = [x for x in curr_standings if x["group"] == group_name]
    sorted_group = sorted(group, key=lambda k: k["points"], reverse=True)
    top_two = sorted_group[0:2]
    return top_two

def get_knockout_match_winner(team_a, team_b):
    exp = get_match_expectation(team_a[ELO], team_b[ELO])
    outcome_float = get_random_float_between(0, 1)
    winner = team_a if (outcome_float < exp) else team_b
    return winner

def sim_knockout_round(curr_standings, master_dict):
    a_top = get_top_two_from(curr_standings, "A")
    b_top = get_top_two_from(curr_standings, "B")
    c_top = get_top_two_from(curr_standings, "C")
    d_top = get_top_two_from(curr_standings, "D")
    e_top = get_top_two_from(curr_standings, "E")
    f_top = get_top_two_from(curr_standings, "F")
    g_top = get_top_two_from(curr_standings, "G")
    h_top = get_top_two_from(curr_standings, "H")

    A1, A2 = a_top
    B1, B2 = b_top
    C1, C2 = c_top
    D1, D2 = d_top
    E1, E2 = e_top
    F1, F2 = f_top
    G1, G2 = g_top
    H1, H2 = h_top

    QF1 = get_knockout_match_winner(A1, B2)
    QF2 = get_knockout_match_winner(C1, D2)
    QF3 = get_knockout_match_winner(E1, F2)
    QF4 = get_knockout_match_winner(G1, H2)
    QF5 = get_knockout_match_winner(B1, A2)
    QF6 = get_knockout_match_winner(D1, C2)
    QF7 = get_knockout_match_winner(F1, E2)
    QF8 = get_knockout_match_winner(H1, G2)

    SF1 = get_knockout_match_winner(QF1, QF2)
    SF2 = get_knockout_match_winner(QF3, QF4)
    SF3 = get_knockout_match_winner(QF5, QF6)
    SF4 = get_knockout_match_winner(QF7, QF8)

    FINAL1 = get_knockout_match_winner(SF1, SF2)
    FINAL2 = get_knockout_match_winner(SF3, SF4)

    CHAMPION = get_knockout_match_winner(FINAL1, FINAL2)

    for i in range(len(master_dict)):
        if master_dict[i]["name"] == CHAMPION["name"]:
            master_dict[i]["champion"] += 1
        if master_dict[i]["name"] == QF1["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF2["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF3["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF4["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF5["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF6["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF7["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == QF8["name"]:
            master_dict[i]["qf"] += 1
        if master_dict[i]["name"] == SF1["name"]:
            master_dict[i]["sf"] += 1
        if master_dict[i]["name"] == SF2["name"]:
            master_dict[i]["sf"] += 1
        if master_dict[i]["name"] == SF3["name"]:
            master_dict[i]["sf"] += 1
        if master_dict[i]["name"] == SF4["name"]:
            master_dict[i]["sf"] += 1

    return master_dict


def update_qualifications(curr_standings, master_dict, name):
    group = [x for x in curr_standings if x["group"] == name]
    sorted_group = sorted(group, key=lambda k: k["points"], reverse=True)
    qualified = sorted_group[0:2]

    first = qualified[0]["name"]
    second = qualified[1]["name"]

    winner_index = -1
    second_index = -1

    for i in range(len(master_dict)):
        if master_dict[i]["name"] == first:
            master_dict[i]["first"] += 1
        if master_dict[i]["name"] == second:
            master_dict[i]["second"] += 1

    return master_dict

def run_sim_n_times(n):
    master_dict = init()
    groups = ["A", "B", "C", "D", "E", "F", "G", "H"]
    update_keys = ["GF", "GA", "points"]

    for i in range(n):
        curr_standings = sim_group_stage()
        for i in range(len(master_dict)):
            team = curr_standings[i]
            for key in update_keys:
                master_dict[i][key] += team[key]

        for group in groups:
            master_dict = update_qualifications(curr_standings, master_dict, group)

        master_dict = sim_knockout_round(curr_standings, master_dict)

    pretty_print(master_dict)

run_sim_n_times(10000)