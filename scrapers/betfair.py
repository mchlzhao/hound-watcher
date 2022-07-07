import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from entities.bookie_type import BookieType
from entities.odds_types import BackLay
from scrapers.scraper import Scraper
from util import process_name


def tab_title_to_name(tab_title: str):
    return BookieType('betfair_' + '_'.join(tab_title.lower().split()))


class BetfairScraper(Scraper):
    def __init__(self, data_store, data_store_lock, url, headless=True,
                 scrape_other_urls=False, scraper_manager=None):
        super().__init__(data_store, data_store_lock, url, headless)

        self.highest_matched = -1
        self.bookie_type = None

        self.scrape_other_urls = scrape_other_urls
        self.scraper_manager = scraper_manager

    def get_bookie_type(self):
        return self.bookie_type

    def setup(self):
        try:
            login_elem = WebDriverWait(self.driver, self.TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//form[@class="ssc-lif"]')))
        except TimeoutException:
            print(f'Loading {self.get_bookie_type()} took too much time!')
            self.stop()
            return

        try:
            tab_elem = WebDriverWait(self.driver, self.TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     './/div[@class="markets-tabs-container"]/ul/li[contains(@class, "selected")]')))
        except TimeoutException:
            print('Could not find selected market tab')
            self.stop()
            return

        self.bookie_type = tab_title_to_name(tab_elem.text)

        if self.scrape_other_urls:
            for url in self.get_other_urls():
                self.scraper_manager.start(url, False)

        (login_elem
         .find_element(by=By.XPATH, value='.//input[@id="ssc-liu"]')
         .send_keys(os.environ['BETFAIR_UN']))
        (login_elem
         .find_element(by=By.XPATH, value='.//input[@id="ssc-lipw"]')
         .send_keys(os.environ['BETFAIR_PW']))
        (login_elem
         .find_element(by=By.XPATH, value='.//input[@id="ssc-lis"]')
         .click())

        time.sleep(5)

    def loop(self):
        try:
            matched = int(WebDriverWait(self.driver, self.TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'total-matched')))
                          .text.split()[1].replace(',', ''))
        except TimeoutException:
            print(f'Loading {self.get_bookie_type()} took too much time!')
            self.stop()
            return

        # if not logged in, pressing 'refresh' may fetch a market state from
        # a prior point in time, which will be reflected in the dollars matched
        # being smaller
        if matched > self.highest_matched:
            self.highest_matched = matched
            data = {'matched': matched, 'markets': {}}

            runners = self.driver.find_elements(
                by=By.XPATH, value='//tr[@class="runner-line"]')
            for runner in runners:
                runner_name = process_name(runner.find_element(
                    by=By.XPATH,
                    value='.//h3[contains(@class, "runner-name")]').text)

                def get_price(e):
                    try:
                        return float(e.text)
                    except ValueError:
                        return None

                prices = [get_price(e) for e in runner.find_elements(
                    by=By.XPATH,
                    value=f'.//td[contains(@class, "last-back-cell") or contains(@class, "first-lay-cell")]//span[@class="bet-button-price"]')]

                # in theory this should not happen
                if prices[0] is not None and prices[1] is not None and \
                        prices[0] > prices[1]:
                    prices[0], prices[1] = prices[1], prices[0]

                data['markets'][runner_name] = BackLay(*prices)

            self.update_data_store(data)

        refresh_button = self.driver.find_element(
            by=By.XPATH, value='.//button[contains(@class, "refresh-btn")]')
        if refresh_button is not None:
            refresh_button.click()

    def get_other_urls(self):
        other_urls = []
        for tab in self.driver.find_elements(
                by=By.XPATH,
                value='.//div[@class="markets-tabs-container"]/ul/li'):
            if 'selected' in tab.get_attribute('class'):
                continue
            if 'Win' in tab.text or 'Places' in tab.text:
                other_urls.append(
                    str(tab.find_element(by=By.XPATH, value='./a')
                        .get_attribute('href')))
        return other_urls
