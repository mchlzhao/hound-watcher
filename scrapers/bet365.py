import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class Bet365Scraper(Scraper):
    def get_name(self):
        return 'bet365'

    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, 
                    '//div[contains(@class, "Market")]/div[contains(@class, "Participant") and contains(@class, "Wrapper") and not(contains(@class, "Scratched"))]')))
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
            self.stop()
            return

        header_elems = self.driver.find_elements(by=By.XPATH,
            value='//div[contains(@class, "InfoBar") and contains(@class, "MarketsHeader")]/*')
        odds_types = [header_elem.text for header_elem in header_elems]
        try:
            fixed_win_index = odds_types.index('Fixed Win')
        except ValueError:
            print("cannot find fixed odds")
        
        data = {}
        for runner_elem in runner_elems:
            name = runner_elem.find_element(by=By.XPATH, value='.//div[contains(@class, "Name")]').text
            # for greyhounds, name may also contain number (2) after
            name = re.sub('\s+\(\d+\)$', '', name)

            odds_elems = runner_elem.find_elements(by=By.XPATH, value='.//span[contains(@class, "Odds")]')
            if len(odds_elems) <= fixed_win_index:
                fixed_win_price = None
            else:
                try:
                    fixed_win_price = float(odds_elems[fixed_win_index].text)
                except ValueError:
                    fixed_win_price = None
            
            print(name, fixed_win_price)
            data[name] = Back(fixed_win_price)
        self.update_data_store(data)
