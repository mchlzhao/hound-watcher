from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time

from config import WEBDRIVER_PATH

class Scraper:
    def __init__(self, data_store, data_store_lock, scraper_name, website, headless=True):
        self._LOOP_PERIOD = 1
        self._TIMEOUT = 10

        self._data_store = data_store
        self._data_store_lock = data_store_lock
        self._scraper_name = scraper_name

        options = Options()
        options.headless = headless
        self._driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)

        self._driver.get(website)
        self.running = False

    def loop(self):
        raise NotImplementedError()

    def run(self):
        self.running = True
        while self.running:
            self.loop()
            time.sleep(self._LOOP_PERIOD)

    def setup(self):
        pass

    def setup_and_run(self):
        self.setup()
        self.run()

    def teardown(self):
        self.running = False
        self._driver.close()

    def update_data_store(self, data):
        self._data_store_lock.acquire()
        self._data_store[self._scraper_name] = data
        self._data_store_lock.release()