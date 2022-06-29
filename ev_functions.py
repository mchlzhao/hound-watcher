BONUS_TO_CASH_RATIO = 0.75
BET_SIZE = 50


def bonus_back_if_place_but_no_win(top_n, odds, prices):
    betfair_win = prices.get('betfair_win')
    betfair_n_place = prices.get(f'betfair_{top_n}_place')
    if any(map(lambda x: x is None, [odds, betfair_win, betfair_n_place])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None or \
            betfair_n_place.mid_prob is None:
        return None

    def ev_given_probs(win_prob, place_prob):
        return odds.back_odds * win_prob + BONUS_TO_CASH_RATIO * (
                place_prob - win_prob) - 1

    ev_per_dollar = ev_given_probs(betfair_win.mid_prob,
                                   betfair_n_place.mid_prob)
    bounds = (ev_given_probs(betfair_win.lay_prob, betfair_n_place.lay_prob),
              ev_given_probs(betfair_win.back_prob, betfair_n_place.back_prob))
    return (ev_per_dollar, *bounds), ev_per_dollar * BET_SIZE


def double_winnings_in_bonus(odds, prices):
    betfair_win = prices.get('betfair_win')
    if odds is None or odds.back_odds is None or betfair_win is None or \
            betfair_win.mid_prob is None:
        return None

    def ev_given_prob(prob):
        return (odds.back_odds + (
                odds.back_odds - 1) * BONUS_TO_CASH_RATIO) * prob - 1

    ev_per_dollar = ev_given_prob(betfair_win.mid_prob)
    bounds = (
        ev_given_prob(betfair_win.lay_prob),
        ev_given_prob(betfair_win.back_prob))
    return (ev_per_dollar, *bounds), ev_per_dollar * BET_SIZE / (
            odds.back_odds - 1)


def no_promotion(odds, prices):
    betfair_win = prices.get('betfair_win')
    if any(map(lambda x: x is None, [odds, betfair_win])):
        return None
    if odds.back_odds is None or betfair_win.mid_prob is None:
        return None

    def ev_given_prob(win_prob):
        return odds.back_odds * win_prob - 1

    ev_per_dollar = ev_given_prob(betfair_win.mid_prob)
    bounds = (
        ev_given_prob(betfair_win.lay_prob),
        ev_given_prob(betfair_win.back_prob))
    return (ev_per_dollar, *bounds), ev_per_dollar * BET_SIZE
