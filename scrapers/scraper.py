from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

from config import WEBDRIVER_PATH

class Scraper:
    def __init__(self, data_store, data_store_lock, scraper_name, url, headless=True):
        self.LOOP_PERIOD = 1
        self.TIMEOUT = 10

        self.data_store = data_store
        self.data_store_lock = data_store_lock
        self.scraper_name = scraper_name
        self.stop_event = None

        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.headless = headless
        self.driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)
        self.driver.get(url)

        print(f'{scraper_name} driver ready')

    def loop(self):
        raise NotImplementedError()

    def setup(self):
        pass

    def setup_and_run(self, stop_event):
        self.stop_event = stop_event
        self.setup()
        while not self.stop_event.is_set():
            print(f'{self.scraper_name} looping')
            self.loop()
            time.sleep(self.LOOP_PERIOD)
        print(f'{self.scraper_name} is shutting down teardown')
        self.driver.close()
        print(f'{self.scraper_name} teardown complete')
    
    def stop(self):
        self.stop_event.set()

    def update_data_store(self, data):
        with self.data_store_lock:
            self.data_store[self.scraper_name] = data