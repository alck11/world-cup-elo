class Match:
    def __init__(self, a_elo, b_elo):
        self.a_elo = a_elo
        self.b_elo = b_elo
        
    def get_expectation(self):
        exponent = (self.b_elo - self.a_elo)/400.0
        return 1/(1 + (10**exponent))