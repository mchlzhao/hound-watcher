class BackLay:
    def __init__(self, back_odds=None, lay_odds=None):
        self.back_odds = back_odds
        self.lay_odds = lay_odds
        self.back_prob = None if back_odds is None else (1 / back_odds)
        self.lay_prob = None if lay_odds is None else (1 / lay_odds)
        self.mid_prob = (None if self.back_odds is None or self.lay_odds is None 
            else ((self.back_prob + self.lay_prob) / 2))
    
    def __str__(self):
        return f'[${self.back_odds} @ ${self.lay_odds}]'

    def __repr__(self):
        return f'BackLay<${self.back_odds} @ ${self.lay_odds}>'

class Back:
    def __init__(self, back_odds=None):
        self.back_odds = back_odds
        self.back_prob = None if back_odds is None else (1 / back_odds)
    
    def __str__(self):
        return f'[${self.back_odds}]'

    def __repr__(self):
        return f'Back<${self.back_odds}>'