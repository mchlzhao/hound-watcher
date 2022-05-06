import os
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from odds_types import Back
from scrapers.scraper import Scraper

class TabScraper(Scraper):
    def get_name(self):
        return 'tab'

    def setup(self):
        self.driver.find_element(by=By.XPATH, value='.//button[@data-testid="header-login"]').click()


        try:
            login_elem = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="login-modal"]')))
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
            self.stop()
            return
        
        (login_elem
            .find_element(by=By.XPATH, value='.//input[@data-testid="account-number-input"]')
            .send_keys(os.environ['TAB_ACCOUNT_NUMBER'])
        )
        (login_elem
            .find_element(by=By.XPATH, value='.//input[@data-testid="password-input"]')
            .send_keys(os.environ['TAB_PASSWORD'])
        )
        (login_elem
            .find_element(by=By.XPATH, value='.//button[@data-testid="login-button"]')
            .click()
        )

        time.sleep(5)

    def loop(self):
        try:
            runner_elems = WebDriverWait(self.driver, self.TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="pseudo-body"]/div[@class="row"]')))
        except TimeoutException:
            print(f'Loading {self.get_name()} took too much time!')
            self.stop()
            return

        data = {}
        for runner_elem in runner_elems:
            name_elem = (runner_elem
                .find_element(by=By.XPATH, value='.//div[@class="runner-name"]'))
            ignore_len = sum([len(child_elem.text) for child_elem in name_elem.find_elements(by=By.XPATH, value='./*')])
            name = name_elem.text[:-ignore_len].strip()

            back_odds_elems = (runner_elem
                .find_elements(by=By.XPATH, value='.//*[@data-test-parimutuel-win-price]/animate-odds-change/div/div'))
            if len(back_odds_elems) == 0:
                back_odds = None
            else:
                try:
                    back_odds = float(back_odds_elems[0].text)
                except:
                    back_odds = None

            data[name] = Back(back_odds)
        self.update_data_store(data)