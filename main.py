import math
import signal
import threading
import time

from functools import partial
from tabulate import tabulate

from ev_functions import bonus_back_if_place_but_no_win, no_promotion
from scrapers.betfair import BetfairScraper
from scrapers.ladbrokes import LadbrokesScraper
from util import process_name

def get_betfair_odds(market_data, name):
    betfair_odds = {}
    for bookie_name, data in market_data.items():
        if 'betfair' in bookie_name:
            betfair_odds[bookie_name] = data['markets'].get(process_name(name))
    return betfair_odds

def analyse_data(market_data, bookie_promotion_types):
    evs = {}
    for bookie_name, data in market_data.items():
        if 'betfair' in bookie_name:
            continue

        evs[bookie_name] = {}
        for runner_name, runner_odds in data.items():
            betfair_odds = get_betfair_odds(market_data, runner_name)
            for i, promo_func in enumerate(bookie_promotion_types.get(bookie_name, [])):
                evs[bookie_name][f'{runner_name} {i}'] = promo_func(runner_odds, betfair_odds)

    return evs

def sigint_handler(signum, frame):
    global running
    for scraper in scrapers:
        scraper.running = False
    for thread in threads:
        thread.join()
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)



betfair_win_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198456732?nodeId=31416879'
betfair_place_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198456737?nodeId=31416879'
ladbrokes_website = 'https://www.ladbrokes.com.au/racing/newmarket-uk/c16d4cf0-00cd-4163-af40-99ecaf2df075'

data_store = {}
data_store_lock = threading.Lock()
scrapers = []
threads = []

scraper_info = [
    ('betfair_win', betfair_win_website, BetfairScraper, True),
    ('betfair_3_place', betfair_place_website, BetfairScraper, True),
    ('ladbrokes', ladbrokes_website, LadbrokesScraper, True)
]

for name, website, scraper_class, headless, in scraper_info:
    scraper = scraper_class(data_store, data_store_lock, name, website, headless)
    scrapers.append(scraper)
    thread = threading.Thread(target=scraper.setup_and_run)
    thread.start()
    threads.append(thread)

bookie_promos = {
    'ladbrokes': [partial(bonus_back_if_place_but_no_win, 3), no_promotion]
}

while True:
    evs = analyse_data(data_store, bookie_promos)
    print('\n' * 10)
    for key in evs:
        print(key)
        print(tabulate(sorted(evs[key].items(), key=lambda x: math.inf if x[1] is None else -x[1]),
            headers=['Name', 'EV'], tablefmt='orgtbl'))
    time.sleep(5)
