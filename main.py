import threading
import time

from scrapers.betfair import BetfairScraper
from scrapers.ladbrokes import LadbrokesScraper

def analyse_data(market_data, bonus_to_cash=0.75):
    if 'betfair_win' not in market_data or 'betfair_place' not in market_data:
        return {}

    win_odds = market_data['betfair_win']['markets']
    place_odds = market_data['betfair_place']['markets']

    evs = {}
    for key in market_data:
        if key in ['betfair_win', 'betfair_place']:
            continue
        evs[key] = {}
        for name, bid_ask in win_odds.items():
            win_prob = 1 / (sum(bid_ask) / 2)
            place_prob = 1 / (sum(place_odds[name]) / 2)

            ev = win_prob * market_data[key][name] + (place_prob - win_prob) * bonus_to_cash - 1
            evs[key][name] = ev
    return evs

# 15:15 bendigo
betfair_win_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198449109?nodeId=31416182'
# 15:15 bendigo
betfair_place_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198449110?nodeId=31416182'
# 15:15 bendigo
ladbrokes_website = 'https://www.ladbrokes.com.au/racing/bendigo/4e300506-9449-446f-9570-79a96d6239b4'

data_store = {}
data_store_lock = threading.Lock()

betfair_win_scraper = BetfairScraper(data_store, data_store_lock, 'betfair_win', betfair_win_website)
betfair_win_thread = threading.Thread(target=betfair_win_scraper.setup_and_run)
betfair_win_thread.start()

betfair_place_scraper = BetfairScraper(data_store, data_store_lock, 'betfair_place', betfair_place_website)
betfair_place_thread = threading.Thread(target=betfair_place_scraper.setup_and_run)
betfair_place_thread.start()

ladbrokes_scraper = LadbrokesScraper(data_store, data_store_lock, 'ladbrokes', ladbrokes_website)
ladbrokes_thread = threading.Thread(target=ladbrokes_scraper.setup_and_run)
ladbrokes_thread.start()

while True:
    print(data_store)
    print(analyse_data(data_store, 0.75))
    time.sleep(1)
