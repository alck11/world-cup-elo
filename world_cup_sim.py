
import random, math
from standings import init
from constants import *
from matches import matches

def get_random_float_between(lower_bound, upper_bound):
    return random.uniform(lower_bound, upper_bound)

def get_match_expectation(rating_a, rating_b):
    exponent = (rating_b - rating_a)/400.0
    return 1/(1 + (10**exponent))

def get_outcome_probabilities(a_elo, b_elo):
    expectation = get_match_expectation(a_elo, b_elo)
    k = 4.0/3.0
    pr_draw = (k * expectation) * (1 - expectation)
    pr_a_win = expectation - (0.5 * pr_draw)
    pr_a_loss = 1 - pr_draw - pr_a_win
    return pr_a_loss, pr_draw

def get_victor_goals(team, goal_indicator, teams):
    mu = teams[team][ATT]
    one_g = poisson_mass(mu, 1)
    two_g = poisson_mass(mu, 2)
    if (goal_indicator < one_g):
        return 1
    elif (goal_indicator < one_g + two_g):
        return 2
    else:
        return 3

def get_loser_goals(team, goals_conceded, goal_indicator, teams):
    if goals_conceded == 1:
        return 0
    if goals_conceded == 2:
        mu = teams[team][ATT]
        one_g = poisson_mass(mu, 1)
        if (goal_indicator < one_g):
            return 0
        else:
            return 1
    if goals_conceded == 3:
        mu = teams[team][ATT]
        one_g = poisson_mass(mu, 1)
        two_g = poisson_mass(mu, 2)
        if (goal_indicator < one_g):
            return 0
        elif (goal_indicator < one_g + two_g):
            return 1
        else:
            return 2

def get_match_score(team_a, team_b, outcome, teams):

    winner_goals_indicator = get_random_float_between(0, 1)
    loser_goals_indicator = get_random_float_between(0, 1)

    # Team A lost
    if outcome == LOSS:
        team_b_goals = get_victor_goals(team_b, winner_goals_indicator, teams)
        team_a_goals = get_loser_goals(team_a, team_b_goals, loser_goals_indicator, teams)
        return [team_a_goals, team_b_goals]
    # Draw
    elif outcome == DRAW:
        mu = teams[team_b][ATT]
        zero_g = poisson_mass(mu, 0)
        one_g = poisson_mass(mu, 1)
        if (winner_goals_indicator < zero_g):
            return [0, 0]
        elif (winner_goals_indicator < zero_g + one_g):
            return [1, 1]
        else:
            return [2, 2]
    # Team A won
    else:
        team_a_goals = get_victor_goals(team_a, winner_goals_indicator, teams)
        team_b_goals = get_loser_goals(team_b, team_a_goals, loser_goals_indicator, teams)
        return [team_a_goals, team_b_goals]

def poisson_mass(mu, n):
    return (mu ** n) * (math.e ** (-mu))/(math.factorial(n))

def get_match_outcome(team_a, team_b, teams):
    a_elo = teams[team_a][ELO]
    b_elo = teams[team_b][ELO]
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

def update_standings(team_a, team_b, a_goals, b_goals, outcome, expectation, teams):
    teams[team_a][GF] += a_goals
    teams[team_a][GA] += b_goals
    teams[team_b][GF] += b_goals
    teams[team_b][GA] += a_goals

    team_a_elo = get_updated_elo(teams[team_a][ELO], expectation, outcome)
    team_b_elo = get_updated_elo(teams[team_b][ELO], 1 - expectation, abs(1 - outcome))

    teams[team_a][ELO] = int(round(team_a_elo))
    teams[team_b][ELO] = int(round(team_b_elo))

    if (a_goals > b_goals):
        teams[team_a][PTS] += 3
    elif (a_goals == b_goals):
        teams[team_a][PTS] += 1
        teams[team_b][PTS] += 1
    else:
        teams[team_b][PTS] += 3

    return teams

def sim_match(team_a, team_b, teams):
    outcome = get_match_outcome(team_a, team_b, teams)
    exp = get_match_expectation(teams[team_a][ELO], teams[team_b][ELO])
    score = get_match_score(team_a, team_b, outcome, teams)
    teams = update_standings(team_a, team_b, score[0], score[1], outcome, exp, teams)
    return teams

def run_sim():
    standings = init()
    for match in matches:
        team_a = match["home"]
        team_b = match["away"]
        standings = sim_match(team_a, team_b, standings)
    return standings

def run_sim_n_times(n):
    for i in range(n):
        run_sim()