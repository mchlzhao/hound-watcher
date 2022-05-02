from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class PointsbetScraper(Scraper):
    def loop(self):
        try:
            runner_elems = WebDriverWait(self._driver, self._TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//div[contains(@data-test, "OutcomeButtonDiv")]')))
        except TimeoutException:
            print(f'Loading {self._scraper_name} took too much time!')
            self.teardown()
            return

        data = {}
        for row_elem in runner_elems:
            name = ' '.join(row_elem
                .find_element(by=By.XPATH, value='./div/div/div/div/span[not(child::*)]/..')
                .text.split(' ')[1:-1])

            win_odds_elem = row_elem.find_elements(by=By.XPATH,
                value='.//button[contains(@data-test, "WinOddsButton")]')
            if len(win_odds_elem) == 0:
                win_price = None
            else:
                win_price = float(win_odds_elem[0]
                    .find_element(by=By.XPATH, value='./span/span/span')
                    .text)

            data[name] = Back(win_price)
        self.update_data_store(data)