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

    def is_betfair(self):
        return self.value in [BookieType.BETFAIR_WIN,
                              BookieType.BETFAIR_2_PLACES,
                              BookieType.BETFAIR_3_PLACES,
                              BookieType.BETFAIR_4_PLACES]

    @classmethod
    def to_betfair_place(cls, n):
        if n == 2:
            return BookieType.BETFAIR_2_PLACES
        if n == 3:
            return BookieType.BETFAIR_3_PLACES
        if n == 4:
            return BookieType.BETFAIR_4_PLACES
        return None
