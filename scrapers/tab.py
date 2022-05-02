from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class TabScraper(Scraper):
    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="pseudo-body"]/div[@class="row"]')))
        except TimeoutException:
            print(f'Loading {self.scraper_name} took too much time!')
            self.teardown()
            return

        data = {}
        for runner_elem in runner_elems:
            name_elem = (runner_elem
                .find_element(by=By.XPATH, value='.//div[@class="runner-name"]'))
            ignore_len = sum([len(child_elem.text) for child_elem in name_elem.find_elements(by=By.XPATH, value='./*')])
            name = name_elem.text[:-ignore_len].strip()

            back_odds_elems = (runner_elem
                .find_elements(by=By.XPATH, value='.//*[@data-test-parimutuel-win-price]/animate/div/div'))
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                back_odds = float(back_odds_elems[0].text)

            data[name] = Back(back_odds)
            print(f'TAB {name} {back_odds}')
        self.update_data_store(data)