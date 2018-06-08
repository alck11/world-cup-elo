from outcomes import *
import random, math
from constants import *

class Match:
    def __init__(self, a_elo, b_elo):
        self.a_elo = a_elo
        self.b_elo = b_elo
        self.outcome = None
        
    def get_expectation(self):
        exponent = (self.b_elo - self.a_elo)/400.0
        return 1/(1 + (10**exponent))

    def get_outcome_probabilities(self):
        exp = self.get_expectation()
        k = 4.0/3.0
        pr_draw = (k * exp) * (1 - exp)
        pr_a_win = exp - (0.5 * pr_draw)
        pr_a_loss = 1 - pr_draw - pr_a_win
        return pr_a_loss, pr_draw

    def get_random_float_between(self, lower_bound, upper_bound):
        return random.uniform(lower_bound, upper_bound)

    def get_outcome(self):
        pr_a_loss, pr_a_draw = self.get_outcome_probabilities()
        outcome_float = self.get_random_float_between(0, 1)
        if outcome_float < pr_a_loss:
            return LOSS
        elif outcome_float < pr_a_loss + pr_a_draw:
            return DRAW
        else:
            return WIN

    def get_score(self):
        result_key = str(self.get_outcome())
        possible_scores = OUTCOMES[result_key]
        return random.choice(possible_scores)