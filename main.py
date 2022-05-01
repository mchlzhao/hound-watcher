import signal
import threading
import time

from tabulate import tabulate

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

def sigint_handler(signum, frame):
    global running
    for scraper in scrapers:
        scraper.running = False
    for thread in threads:
        thread.join()
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)



# 18:29 mandurah r1
betfair_win_website = 'https://www.betfair.com.au/exchange/plus/greyhound-racing/market/1.198503122?nodeId=31419158'
betfair_place_website = 'https://www.betfair.com.au/exchange/plus/greyhound-racing/market/1.198503123?nodeId=31419158'
ladbrokes_website = 'https://www.ladbrokes.com.au/racing/mandurah/e407b7fb-457a-4c70-935c-717fef4daab1'

data_store = {}
data_store_lock = threading.Lock()
scrapers = []
threads = []

scraper_info = [
    ('betfair_win', betfair_win_website, BetfairScraper, True),
    ('betfair_place', betfair_place_website, BetfairScraper, True),
    ('ladbrokes', ladbrokes_website, LadbrokesScraper, False)
]

for name, website, scraper_class, headless, in scraper_info:
    scraper = scraper_class(data_store, data_store_lock, name, website, headless)
    scrapers.append(scraper)
    thread = threading.Thread(target=scraper.setup_and_run)
    thread.start()
    threads.append(thread)

while True:
    evs = analyse_data(data_store, 0.75)
    for key in evs:
        print('\n' * 10)
        print(key)
        print(tabulate(sorted(evs[key].items(), key=lambda x: -x[1]), headers=['Name', 'EV']))
    time.sleep(5)
