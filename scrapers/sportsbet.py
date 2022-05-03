from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class SportsbetScraper(Scraper):
    def loop(self):
        print(f'{self.scraper_name} in loop')
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, ('//div[@data-automation-id="racecard-body"]'
                     '/div[contains(@data-automation-id, "racecard-outcome")]'))))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        data = {}
        for runner_elem in runner_elems:
            name_elems = runner_elem.find_elements(by=By.XPATH,
                value='.//div[contains(@data-automation-id, "racecard-outcome-name")]/span')
            if len(name_elems) == 0:
                continue

            name = ' '.join(name_elems[0].text.split(' ')[1:])

            back_odds_elems = (runner_elem.find_elements(by=By.XPATH,
                value=('.//div[contains(@data-automation-id, "racecard-outcome-0")]'
                    '//span[@data-automation-id="price-text"]')))
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                back_odds = float(back_odds_elems[0].text)
            
            data[name] = Back(back_odds)
        self.update_data_store(data)
        print(f'{self.scraper_name} out of loop')