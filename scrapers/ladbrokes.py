from selenium.webdriver.common.by import By

from entities.odds_types import Back
from scrapers.scraper import Scraper


class LadbrokesScraper(Scraper):
    def get_name(self):
        return 'ladbrokes'

    def loop(self):
        data = {}
        for row_elem in self.driver.find_elements(
                by=By.XPATH,
                value='//table[not(contains(@class, "resulted"))]//tr[contains(@class, "race-table-row") and not(contains(@class, "scratched"))]'):
            name = row_elem.find_element(by=By.CLASS_NAME,
                                         value='runner-name').text

            back_odds = float(row_elem.find_element(
                by=By.XPATH,
                value='.//span[@data-testid="price-button-odds"]').text)

            data[name] = Back(back_odds)

        self.update_data_store(data)
