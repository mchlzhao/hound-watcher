import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from entities.odds_types import Back
from scrapers.scraper import Scraper


class BetdeluxeScraper(Scraper):
    def get_name(self):
        return 'betdeluxe'

    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, 2 * self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH,
                                                       '//li[contains(@class, "RaceSelectionsListItem")]/div[contains(@class, "RaceSelectionsListItem")]')))
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
            self.stop()
            return

        header_elems = self.driver.find_elements(by=By.XPATH,
                                                 value='//div[contains(@class, "HeaderRow-RaceSelectionsList")]/div[contains(@class, "RaceSelectionsList")]')
        odds_types = [header_elem.text for header_elem in header_elems]
        try:
            fixed_win_index = odds_types.index('Fixed (W)')
        except ValueError:
            print("cannot find fixed odds")

        data = {}
        for runner_elem in runner_elems:
            name = runner_elem.find_element(by=By.XPATH,
                                            value='.//div[contains(@class, "Name-RaceSelectionDetails")]').text
            # will contain "1." preceding and "(2)" succeeding
            name = re.sub('^\d+\.\s+', '', name)
            name = re.sub('\s+\(\d+\)$', '', name)

            fixed_win_price_elems = runner_elem.find_elements(by=By.XPATH,
                                                              value=f'./div[contains(@data-fs-title, "{fixed_win_index}-price_button")]')
            if len(fixed_win_price_elems) == 0:
                fixed_win_price = None
            else:
                try:
                    fixed_win_price = float(fixed_win_price_elems[0].text)
                except ValueError:
                    fixed_win_price = None

            data[name] = Back(fixed_win_price)
        self.update_data_store(data)
