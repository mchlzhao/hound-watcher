from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class SportsbetScraper(Scraper):
    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, ('//div[@data-automation-id="racecard-body"]'
                     '/div[contains(@data-automation-id, "racecard-outcome")]'))))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.teardown()
            return

        data = {}
        for row_elem in runner_elems:
            name_elems = row_elem.find_elements(by=By.XPATH,
                value='.//div[contains(@data-automation-id, "racecard-outcome-name")]/span')
            if len(name_elems) == 0:
                continue

            name = ' '.join(name_elems[0].text.split(' ')[1:])

            win_odds_elem = (row_elem.find_elements(by=By.XPATH,
                value=('.//div[contains(@data-automation-id, "racecard-outcome-0")]'
                    '//span[@data-automation-id="price-text"]')))
            if len(win_odds_elem) == 0:
                win_price = None
            else:
                win_price = float(win_odds_elem[0].text)
            
            data[name] = Back(win_price)
        self.update_data_store(data)