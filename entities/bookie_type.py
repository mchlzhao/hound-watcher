from enum import Enum


class BookieType(str, Enum):
    BET365 = 'bet365'
    BETDELUXE = 'betdeluxe'
    BETFAIR_WIN = 'betfair_win'
    BETFAIR_2_PLACES = 'betfair_2_places'
    BETFAIR_3_PLACES = 'betfair_3_places'
    BETFAIR_4_PLACES = 'betfair_4_places'
    BETFAIR = [BETFAIR_WIN, BETFAIR_2_PLACES, BETFAIR_3_PLACES,
               BETFAIR_4_PLACES]
    BLUEBET = 'bluebet'
    LADBROKES = 'ladbrokes'
    PALMERBET = 'palmerbet'
    POINTSBET = 'pointsbet'
    SPORTSBET = 'sportsbet'
    TAB = 'tab'
