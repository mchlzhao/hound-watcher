from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from entities.bookie_type import BookieType
from entities.odds_types import Back
from scrapers.scraper import Scraper


class PointsbetScraper(Scraper):
    def get_bookie_type(self):
        return BookieType.POINTSBET

    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH,
                                                       '//div[contains(@data-test, "OutcomeButtonDiv")]')))
        except TimeoutException:
            print(f'Loading {self.get_bookie_type()} took too much time!')
            self.stop()
            return

        data = {}
        for runner_elem in runner_elems:
            name = ' '.join(runner_elem
                            .find_element(by=By.XPATH,
                                          value='./div/div/div/div/span[not(child::*)]/..')
                            .text.split(' ')[1:-1])

            back_odds_elems = runner_elem.find_elements(by=By.XPATH,
                                                        value='.//button[contains(@data-test, "WinOddsButton")]')
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                back_odds = float(back_odds_elems[0]
                                  .find_element(by=By.XPATH,
                                                value='./span/span/span')
                                  .text)

            data[name] = Back(back_odds)
        self.update_data_store(data)
