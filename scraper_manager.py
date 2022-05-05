import threading

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
        self.threads_by_name = {}
    
    @staticmethod
    def url_to_scraper_class(url):
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
    
    def start(self, name, url):
        scraper_class = ScraperManager.url_to_scraper_class(url)
        if scraper_class is None:
            print(f'don\'t know how to scrape {url=}')
            return
        if name in self.threads_by_name:
            print(f'{name=} already in use')
            return
        
        thread = scraper_class(self.data_store, self.data_store_lock, name, url, True)
        thread.start()
        self.threads_by_name[name] = thread
    
    def stop(self, name):
        if name not in self.threads_by_name:
            print(f'no running thread with {name=}')
            return
        
        thread = self.threads_by_name.pop(name)
        thread.stop()
        thread.join()
    
    def stop_all(self):
        names = list(self.threads_by_name.keys())
        for name in names:
            self.stop(name)