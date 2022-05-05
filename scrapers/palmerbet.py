import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class PalmerbetScraper(Scraper):
    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//tr/app-race-runner/div[not(contains(@class, "scratched"))]')))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.stop()
            return

        data = {}
        for runner_elem in runner_elems:
            name_elem = (runner_elem
                .find_element(by=By.XPATH, value='.//div[contains(@class, "runner-title")]'))
            ignore_len = sum([len(child_elem.text) for child_elem in name_elem.find_elements(by=By.XPATH, value='./*')])
            # palmerbet puts a number "1. " in front of runner name, and puts another number " (2)" in a child span
            name = ' '.join(name_elem.text[:-ignore_len].strip().split(' ')[1:])
            # some names have " (Em{x})" after their names, where {x} is a number
            name = re.sub('\s*\(.*\)$', '', name)

            back_odds_elems = (runner_elem
                .find_elements(by=By.XPATH, value='.//td[not(contains(@class, "place"))]//app-price-display/span'))
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                back_odds = float(back_odds_elems[0].text)

            data[name] = Back(back_odds)
        self.update_data_store(data)