from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import os
import time

from odds_types import BackLay
from scrapers.scraper import Scraper
from util import process_name

class BetfairScraper(Scraper):
    def __init__(self, data_store, data_store_lock, scraper_name, url, stop_event, headless=True):
        super().__init__(data_store, data_store_lock, scraper_name, url, stop_event, headless)

        self.highest_matched = -1

    def setup(self):
        try:
            elems = (WebDriverWait(self.driver, self.TIMEOUT)
                .until(EC.visibility_of_all_elements_located((By.XPATH, '//form[@class="ssc-lif"]'))))
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        (elem
            .find_element(by=By.XPATH, value='.//input[@id="ssc-liu"]')
            .send_keys(os.environ['BETFAIR_UN']))
        (elem
            .find_element(by=By.XPATH, value='.//input[@id="ssc-lipw"]')
            .send_keys(os.environ['BETFAIR_PW']))
        (elem
            .find_element(by=By.XPATH, value='.//input[@id="ssc-lis"]')
            .click())
        
        time.sleep(5)

    def loop(self):
        try:
            elem = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class, "main-mv-container")]')))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        try:
            matched = int(WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.XPATH, './/span[@class="total-matched"]')))
                .text.split()[1].replace(',', ''))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        if matched > self.highest_matched:
            self.highest_matched = matched
            data = {}
            data['matched'] = matched
            data['markets'] = {}

            runners = (elem
                .find_elements(by=By.XPATH, value='.//tr[@class="runner-line"]'))
            for runner in runners:
                runner_name = process_name(runner
                    .find_element(by=By.XPATH, value='.//h3[contains(@class, "runner-name")]')
                    .text)
                def get_price(text):
                    val = (runner
                        .find_element(by=By.XPATH, value=f'.//td[contains(@class, "{text}-cell")]')
                        .find_element(by=By.XPATH, value='.//span[@class="bet-button-price"]')
                        .text)
                    try:
                        return float(val)
                    except ValueError:
                        return None
                data['markets'][runner_name] = BackLay(get_price('last-back'), get_price('first-lay'))

            self.update_data_store(data)

        refresh_button = elem.find_element(by=By.XPATH, value='.//button[contains(@class, "refresh-btn")]')
        refresh_button.click()