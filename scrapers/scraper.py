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

        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.headless = headless
        self.driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)

        self.driver.get(url)
        self.running = False

        print(f'{scraper_name} driver ready')

    def loop(self):
        raise NotImplementedError()

    def run(self):
        self.running = True
        while self.running:
            self.loop()
            time.sleep(self.LOOP_PERIOD)
        self.teardown()

    def setup(self):
        pass

    def setup_and_run(self):
        self.setup()
        self.run()

    def teardown(self):
        self.running = False
        self.driver.close()

    def update_data_store(self, data):
        self.data_store_lock.acquire()
        self.data_store[self.scraper_name] = data
        self.data_store_lock.release()