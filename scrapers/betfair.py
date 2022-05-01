from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import os
import time

from scrapers.scraper import Scraper

class BetfairScraper(Scraper):
    def __init__(self, data_store, data_store_lock, scraper_name, website):
        super().__init__(data_store, data_store_lock, scraper_name, website)

        self.highest_matched = -1

    def setup(self):
        try:
            elems = (WebDriverWait(self._driver, self._TIMEOUT)
                .until(EC.visibility_of_all_elements_located((By.XPATH, '//form[@class="ssc-lif"]'))))
            print("Page is ready!")
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {self._scraper_name} took too much time!')
            self.teardown()
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
            elems = WebDriverWait(self._driver, self._TIMEOUT).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "main-mv-container")]')))
            print("Page is ready!")
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.teardown()
            return

        matched = int(elem
            .find_element(by=By.XPATH, value='.//span[@class="total-matched"]')
            .text.split()[1].replace(',', ''))

        if matched > self.highest_matched:
            self.highest_matched = matched
            data = {}
            data['matched'] = matched
            data['markets'] = {}

            runners = (elem
                .find_elements(by=By.XPATH, value='.//tr[@class="runner-line"]'))
            for runner in runners:
                runner_name = runner.find_element(by=By.XPATH, value='.//h3[contains(@class, "runner-name")]').text
                def get_price(text):
                    val = (runner
                        .find_element(by=By.XPATH, value=f'.//td[contains(@class, "{text}-cell")]')
                        .find_element(by=By.XPATH, value='.//span[@class="bet-button-price"]')
                        .text)
                    try:
                        return float(val)
                    except ValueError:
                        return None
                data['markets'][runner_name] = (get_price('last-back'), get_price('first-lay'))
            
            self.update_data_store(data)

        refresh_button = elem.find_element(by=By.XPATH, value='.//button[contains(@class, "refresh-btn")]')
        refresh_button.click()