import threading

from scrapers.bet365 import Bet365Scraper
from scrapers.betdeluxe import BetdeluxeScraper
from scrapers.betfair import BetfairScraper
from scrapers.bluebet import BluebetScraper
from scrapers.ladbrokes import LadbrokesScraper
from scrapers.palmerbet import PalmerbetScraper
from scrapers.pointsbet import PointsbetScraper
from scrapers.sportsbet import SportsbetScraper
from scrapers.tab import TabScraper


class ScraperManager:
    def __init__(self, data_store):
        self.data_store = data_store
        self.data_store_lock = threading.Lock()
        self.threads_by_url = {}

    @staticmethod
    def url_to_scraper_class(url):
        if 'bet365' in url:
            return Bet365Scraper
        if 'betdeluxe' in url:
            return BetdeluxeScraper
        if 'betfair' in url:
            return BetfairScraper
        if 'bluebet' in url:
            return BluebetScraper
        if 'ladbrokes' in url:
            return LadbrokesScraper
        if 'palmerbet' in url:
            return PalmerbetScraper
        if 'pointsbet' in url:
            return PointsbetScraper
        if 'sportsbet' in url:
            return SportsbetScraper
        if 'tab' in url:
            return TabScraper
        return None

    def start(self, url):
        scraper_class = ScraperManager.url_to_scraper_class(url)
        if scraper_class is None:
            print(f'don\'t know how to scrape {url=}')
            return
        if url in self.threads_by_url:
            print(f'{url=} already being scraped')
            return

        thread = scraper_class(self.data_store, self.data_store_lock, url,
                               headless=scraper_class != Bet365Scraper)
        thread.start()
        self.threads_by_url[url] = thread

    def stop(self, url):
        if url not in self.threads_by_url:
            print(f'no running thread with {url=}')
            return

        thread = self.threads_by_url.pop(url)
        thread.stop()
        thread.join()

    def stop_all(self):
        names = list(self.threads_by_url.keys())
        for name in names:
            self.stop(name)
