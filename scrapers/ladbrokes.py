import time

from selenium.webdriver.common.by import By

from odds_types import Back
from scrapers.scraper import Scraper


class LadbrokesScraper(Scraper):
    def get_name(self):
        return 'ladbrokes'

    def loop(self):
        data = {}
        for row_elem in self.driver.find_elements(
                by=By.XPATH,
                value='//table[not(contains(@class, "resulted"))]//tr[contains(@class, "race-table-row") and not(contains(@class, "scratched"))]'):
            name = row_elem.find_element(by=By.CLASS_NAME,
                                         value='runner-name').text

            back_odds = float(row_elem.find_element(
                by=By.XPATH,
                value='.//span[@data-testid="price-button-odds"]').text)

            data[name] = Back(back_odds)

        self.update_data_store(data)

    def go_to_round(self, round_num):
        links = self.driver.find_elements(
            by=By.XPATH, value='//ul[@class="race-switcher-list"]/li/a')
        for link in links:
            if round_num == int(link.text):
                link.click()
                break
        else:
            print(f'could not find {round_num=}')
            return

        time.sleep(5)
