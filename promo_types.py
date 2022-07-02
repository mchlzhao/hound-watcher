from dataclasses import dataclass
from typing import Tuple, Type

BONUS_TO_CASH_RATIO = 0.75
BET_SIZE = 50


class PromoType:
    def get_ev_info(self, bookie, runner_name):
        raise NotImplementedError()


@dataclass
class EVInfo:
    bookie: str
    runner_name: str
    bookie_odds: float
    promo_type: Type[PromoType]
    ev_per_dollar: float
    ev_per_dollar_bounds: Tuple[float, float]
    bet_amount: float
    ev_of_bet: float


class BonusBackIfPlaceButNoWin(PromoType):
    def __init__(self, data_store, top_n, *,
                 bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                 bet_limit=None,
                 winnings_limit=None):
        self.data_store = data_store
        self.top_n = top_n
        self.bonus_to_cash_ratio = bonus_to_cash_ratio
        self.bet_limit = bet_limit
        self.winnings_limit = winnings_limit
        assert (bet_limit is None) != (winnings_limit is None)

    def ev_given_probs(self, bookie_odds, win_prob, place_prob):
        return bookie_odds * win_prob + self.bonus_to_cash_ratio * (
                place_prob - win_prob) - 1

    def get_ev_info(self, bookie, runner_name):
        betfair_win = self.data_store.get_odds('betfair_win', runner_name)
        betfair_n_place = self.data_store.get_odds(
            f'betfair_{self.top_n}_place', runner_name)
        bookie_win = self.data_store.get_odds(bookie, runner_name)

        if any(map(lambda x: x is None,
                   [bookie_win, betfair_win, betfair_n_place])):
            return None
        if bookie_win.back_odds is None or betfair_win.mid_prob is None or \
                betfair_n_place.mid_prob is None:
            return None

        ev_per_dollar = self.ev_given_probs(bookie_win.back_odds,
                                            betfair_win.mid_prob,
                                            betfair_n_place.mid_prob)
        ev_per_dollar_bounds = (
            self.ev_given_probs(bookie_win.back_odds, betfair_win.lay_prob,
                                betfair_n_place.lay_prob),
            self.ev_given_probs(bookie_win.back_odds, betfair_win.back_prob,
                                betfair_n_place.back_prob))

        if ev_per_dollar > 0:
            bet_amount = self.bet_limit if self.bet_limit is not None else \
                self.winnings_limit / (bookie_win.back_odds - 1)
        else:
            bet_amount = 0

        return EVInfo(bookie, runner_name, bookie_win.back_odds, self.__class__,
                      ev_per_dollar, ev_per_dollar_bounds, bet_amount,
                      ev_per_dollar * bet_amount)


class BonusBackEqualToWinnings(PromoType):
    def __init__(self, data_store, *,
                 bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                 bet_limit=None,
                 winnings_limit=None):
        self.data_store = data_store
        self.bonus_to_cash_ratio = bonus_to_cash_ratio
        self.bet_limit = bet_limit
        self.winnings_limit = winnings_limit
        assert (bet_limit is None) != (winnings_limit is None)

    def ev_given_prob(self, bookie_odds, win_prob):
        return (bookie_odds + (bookie_odds - 1) * self.bonus_to_cash_ratio) * \
               win_prob - 1

    def get_ev_info(self, bookie, runner_name):
        betfair_win = self.data_store.get_odds('betfair_win', runner_name)
        bookie_win = self.data_store.get_odds(bookie, runner_name)
        if bookie_win is None or bookie_win.back_odds is None or \
                betfair_win is None or betfair_win.mid_prob is None:
            return None

        ev_per_dollar = self.ev_given_prob(bookie_win.back_odds,
                                           betfair_win.mid_prob)
        ev_per_dollar_bounds = (
            self.ev_given_prob(bookie_win.back_odds, betfair_win.lay_prob),
            self.ev_given_prob(bookie_win.back_odds, betfair_win.back_prob))

        if ev_per_dollar > 0:
            bet_amount = self.bet_limit if self.bet_limit is not None else \
                self.winnings_limit / (bookie_win.back_odds - 1)
        else:
            bet_amount = 0

        return EVInfo(bookie, runner_name, bookie_win.back_odds, self.__class__,
                      ev_per_dollar, ev_per_dollar_bounds, bet_amount,
                      ev_per_dollar * bet_amount)


class NoPromo(PromoType):
    def __init__(self, data_store, *,
                 bet_limit=None,
                 winnings_limit=None):
        self.data_store = data_store
        self.bet_limit = bet_limit
        self.winnings_limit = winnings_limit
        assert (bet_limit is None) != (winnings_limit is None)

    def ev_given_probs(self, bookie_odds, win_prob):
        return bookie_odds * win_prob - 1

    def get_ev_info(self, bookie, runner_name):
        betfair_win = self.data_store.get_odds('betfair_win', runner_name)
        bookie_win = self.data_store.get(bookie, runner_name)
        if any(map(lambda x: x is None, [bookie_win.back_odds, betfair_win])):
            return None
        if bookie_win.back_odds is None or betfair_win.mid_prob is None:
            return None

        ev_per_dollar = self.ev_given_probs(bookie_win, betfair_win.mid_prob)
        ev_per_dollar_bounds = (
            self.ev_given_probs(bookie_win, betfair_win.lay_prob),
            self.ev_given_probs(bookie_win, betfair_win.back_prob))

        if ev_per_dollar > 0:
            bet_amount = self.bet_limit if self.bet_limit is not None else \
                self.winnings_limit / (bookie_win.back_odds - 1)
        else:
            bet_amount = 0

        return EVInfo(bookie, runner_name, bookie_win.back_odds, self.__class__,
                      ev_per_dollar, ev_per_dollar_bounds, bet_amount,
                      ev_per_dollar * bet_amount)


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
    bounds = (
        ev_given_probs(betfair_win.lay_prob, betfair_n_place.lay_prob),
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
