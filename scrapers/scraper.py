import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import WEBDRIVER_PATH

class Scraper(threading.Thread):
    def __init__(self, data_store, data_store_lock, url, headless=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.LOOP_PERIOD = 1
        self.TIMEOUT = 10

        self.data_store = data_store
        self.data_store_lock = data_store_lock
        self.stop_event = threading.Event()

        self.url = url
        self.headless = headless

    def get_name(self):
        raise NotImplementedError()

    def loop(self):
        raise NotImplementedError()

    def setup(self):
        pass

    def run(self):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.headless = self.headless
        self.driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)
        self.driver.get(self.url)
        print(f'{self.url} driver ready')

        self.setup()
        while not self.stop_event.is_set():
            try:
                self.loop()
            except Exception as e:
                print(e)
                with self.data_store_lock:
                    self.data_store.pop(self.get_name())
            time.sleep(self.LOOP_PERIOD)
        with self.data_store_lock:
            self.data_store.pop(self.get_name())
        self.driver.close()
    
    def stop(self):
        self.stop_event.set()

    def update_data_store(self, data):
        with self.data_store_lock:
            self.data_store[self.get_name()] = data
