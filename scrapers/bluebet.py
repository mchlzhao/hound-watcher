import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class BluebetScraper(Scraper):
    def get_name(self):
        return 'bluebet'

    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//div/a/div[contains(@class, "null")]')))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        data = {}
        for runner_elem in runner_elems:
            name_elems = runner_elem.find_elements(by=By.XPATH, value='./div/div/div[contains(@class, "null")]')
            if len(name_elems) == 0:
                continue
            # will contain "1." preceding and "(2)" succeeding
            name = re.sub('^\d+\.\s+', '', name_elems[0].text)
            name = re.sub('\s+\(\d+\)$', '', name)

            back_odds_elems = runner_elem.find_elements(by=By.XPATH, value='.//span[@class="MuiButton-label"]/div')
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                back_odds = float(back_odds_elems[0].text)
            
            data[name] = Back(back_odds)
        self.update_data_store(data, self.name)