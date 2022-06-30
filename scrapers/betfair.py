import os
import re
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from odds_types import BackLay
from scrapers.scraper import Scraper
from util import process_name


def tab_title_to_name(tab_title: str):
    return 'betfair_' + '_'.join(tab_title.lower().split())


class BetfairScraper(Scraper):
    def __init__(self, data_store, data_store_lock, url, headless=True,
                 scrape_other_urls=False, scraper_manager=None):
        super().__init__(data_store, data_store_lock, url, headless)

        self.highest_matched = -1
        self.name = 'betfair'

        self.scrape_other_urls = scrape_other_urls
        self.scraper_manager = scraper_manager

    def get_name(self):
        return self.name

    def setup(self):
        try:
            elem = (WebDriverWait(self.driver, self.TIMEOUT)
                .until(ec.presence_of_element_located(
                (By.XPATH, '//form[@class="ssc-lif"]'))))
            market_name_first_word = (WebDriverWait(self.driver, self.TIMEOUT)
                .until(ec.presence_of_element_located(
                (By.XPATH, '//span[@class="market-name"]')))
                .text.strip().split()[0])
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
            self.stop()
            return

        selected_tab_title = self.driver.find_element(
            by=By.XPATH,
            value='.//div[@class="markets-tabs-container"]/ul/li[contains(@class, "selected")]').text
        self.name = tab_title_to_name(selected_tab_title)

        if self.scrape_other_urls:
            for _, url in self.get_other_urls():
                self.scraper_manager.start(url, False)

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
            matched = int(WebDriverWait(self.driver, self.TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'total-matched')))
                          .text.split()[1].replace(',', ''))
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
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

    def get_other_urls(self, include_cur=False, return_elements=False):
        other_urls = []
        for tab in self.driver.find_elements(
                by=By.XPATH,
                value='.//div[@class="markets-tabs-container"]/ul/li/a'):
            if 'selected' in tab.find_element(
                    by=By.XPATH, value='..').get_attribute('class') and \
                    not include_cur:
                continue
            if 'Win' in tab.text or 'Places' in tab.text:
                other_urls.append((
                    tab.text,
                    tab if return_elements else str(tab.get_attribute('href'))
                ))
        return other_urls

    def go_to_round(self, round_num):
        links = self.driver.find_elements(
            by=By.XPATH,
            value='.//ul[contains(@class, "active-section")]/li/a[contains(@class, "navigation-link") and not(contains(@class, "disabled"))]')
        for link in links:
            round_num_match = re.search(' R(\d+) ', link.text)
            if round_num_match is None:
                continue
            if round_num == int(round_num_match.group(1)):
                link.click()
                break
        else:
            print(f'could not find {round_num=}')
            return

        time.sleep(5)

        all_tabs = self.get_other_urls(include_cur=True, return_elements=True)
        for title, tab in all_tabs:
            if tab_title_to_name(title) == self.name:
                tab.click()
                break
        else:
            print(f'cound not find tab corresponding to {self.name=}')
            return

        time.sleep(5)
