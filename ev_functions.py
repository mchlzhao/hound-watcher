BONUS_TO_CASH_RATIO = 0.75
BET_SIZE = 50

def bonus_back_if_place_but_no_win(top_n, odds, prices):
    betfair_win = prices.get('betfair_win')
    betfair_n_place = prices.get(f'betfair_{top_n}_place')
    if any(map(lambda x: x is None, [odds, betfair_win, betfair_n_place])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None or betfair_n_place.mid_prob is None:
        return None

    ev_per_dollar = odds.back_odds * betfair_win.mid_prob + BONUS_TO_CASH_RATIO * (betfair_n_place.mid_prob - betfair_win.mid_prob) - 1
    return (ev_per_dollar, ev_per_dollar * BET_SIZE)

def double_winnings_in_bonus(odds, prices):
    betfair_win = prices.get('betfair_win')
    if odds is None or odds.back_odds is None or betfair_win is None or betfair_win.mid_prob is None:
        return None
    ev_per_dollar = (odds.back_odds + (odds.back_odds - 1) * BONUS_TO_CASH_RATIO) * betfair_win.mid_prob - 1
    return (ev_per_dollar, ev_per_dollar * BET_SIZE / (odds.back_odds - 1))

def no_promotion(odds, prices):
    betfair_win = prices.get('betfair_win')
    if any(map(lambda x: x is None, [odds, betfair_win])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None:
        return None

    ev_per_dollar = odds.back_odds * betfair_win.mid_prob - 1
    return (ev_per_dollar, ev_per_dollar * BET_SIZE)