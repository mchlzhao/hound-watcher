import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import WEBDRIVER_PATH

class Scraper(threading.Thread):
    def __init__(self, data_store, data_store_lock, scraper_name, url, headless=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.LOOP_PERIOD = 1
        self.TIMEOUT = 10

        self.data_store = data_store
        self.data_store_lock = data_store_lock
        self.scraper_name = scraper_name
        self.stop_event = threading.Event()

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

    def run(self):
        self.setup()
        while not self.stop_event.is_set():
            self.loop()
            time.sleep(self.LOOP_PERIOD)
        self.driver.close()
    
    def stop(self):
        self.stop_event.set()

    def update_data_store(self, data):
        with self.data_store_lock:
            self.data_store[self.scraper_name] = data