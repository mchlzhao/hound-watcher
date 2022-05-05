from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class LadbrokesScraper(Scraper):
    def loop(self):
        try:
            elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//table[contains(@class, "race-table")]')))
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        data = {}
        for row_elem in elem.find_elements(by=By.XPATH, value='.//tr[contains(@class, "race-table-row")]'):
            name = (row_elem
                .find_element(by=By.XPATH, value='.//span[@class="runner-name"]')
                .text)

            fixed_odds_elem = row_elem.find_elements(by=By.XPATH, value='.//td[contains(@class, "runner-fixed-odds")]')
            if len(fixed_odds_elem) == 0:
                back_odds = None
            else:
                back_odds = float(fixed_odds_elem[0]
                    .find_element(by=By.XPATH, value='.//span[@data-testid="price-button-odds"]')
                    .text)
            
            data[name] = Back(back_odds)
        self.update_data_store(data)