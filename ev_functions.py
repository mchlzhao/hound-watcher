BONUS_TO_CASH_RATIO = 0.75

def bonus_back_if_place_but_no_win(top_n, odds, prices):
    betfair_win = prices.get('betfair_win')
    betfair_n_place = prices.get(f'betfair_{top_n}_place')
    if any(map(lambda x: x is None, [odds, betfair_win, betfair_n_place])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None or betfair_n_place.mid_prob is None:
        return None

    return odds.back_odds * betfair_win.mid_prob + BONUS_TO_CASH_RATIO * (betfair_n_place.mid_prob - betfair_win.mid_prob) - 1

def no_promotion(odds, prices):
    betfair_win = prices.get('betfair_win')
    if any(map(lambda x: x is None, [odds, betfair_win])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None:
        return None

    return odds.back_odds * betfair_win.mid_prob - 1