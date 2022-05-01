from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import os
import threading
import time

market_data = {}

def scrape_odds_betfair(website, market_name, lock):
    global market_data
    driver = webdriver.Chrome(path)
    driver.get(website)

    delay = 5
    try:
        elems = WebDriverWait(driver, delay).until(
            EC.visibility_of_all_elements_located(
                (By.XPATH, '//form[@class="ssc-lif"]')))
        print("Page is ready!")
        elem = elems[0]
    except TimeoutException:
        print(f'Loading {website} took too much time!')
        driver.close()
        return
    
    (elem
        .find_element(by=By.XPATH, value='.//input[@id="ssc-liu"]')
        .send_keys(os.environ['BETFAIR_UN']))
    (elem
        .find_element(by=By.XPATH, value='.//input[@id="ssc-lipw"]')
        .send_keys(os.environ['BETFAIR_PW']))
    (elem
        .find_element(by=By.XPATH, value='.//input[@id="ssc-lis"]')
        .click())
    time.sleep(5)

    highest_matched = -1

    def f(depth):
        delay = 5 # seconds
        try:
            elems = WebDriverWait(driver, delay).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "main-mv-container")]')))
            print("Page is ready!")
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {website} took too much time!')
            driver.close()
            return

        matched = int(elem
            .find_element(by=By.XPATH, value='.//span[@class="total-matched"]')
            .text.split()[1].replace(',', ''))
        nonlocal highest_matched
        if matched > highest_matched:
            highest_matched = matched
            data = {}
            data['matched'] = matched
            data['markets'] = {}

            runners = (elem
                .find_elements(by=By.XPATH, value='.//tr[@class="runner-line"]'))
            for runner in runners:
                runner_name = runner.find_element(by=By.XPATH, value='.//h3[contains(@class, "runner-name")]').text
                def get_price(text):
                    val = (runner
                        .find_element(by=By.XPATH, value=f'.//td[contains(@class, "{text}-cell")]')
                        .find_element(by=By.XPATH, value='.//span[@class="bet-button-price"]')
                        .text)
                    try:
                        return float(val)
                    except ValueError:
                        return None
                data['markets'][runner_name] = (get_price('last-back'), get_price('first-lay'))
            lock.acquire()
            market_data[market_name] = data
            lock.release()
            
        refresh_button = elem.find_element(by=By.XPATH, value='.//button[contains(@class, "refresh-btn")]')
        refresh_button.click()

        time.sleep(1)

        if depth < 100:
            f(depth+1)

    f(0)
    driver.close()

def scrape_odds_ladbrokes(website):
    driver = webdriver.Chrome(path)
    driver.get(website)

    def f(depth):
        delay = 5 # seconds
        try:
            elems = WebDriverWait(driver, delay).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//table[contains(@class, "race-table")]')))
            print("Page is ready!")
            elem = elems[0]
        except TimeoutException:
            print(f'Loading {website} took too much time!')
            driver.close()
            return

        for row_elem in elem.find_elements(by=By.XPATH, value='.//tr[contains(@class, "race-table-row")]'):
            name = (row_elem
                .find_element(by=By.XPATH, value='.//span[@class="runner-name"]')
                .text)

            fixed_odds_elem = row_elem.find_elements(by=By.XPATH, value='.//td[contains(@class, "runner-fixed-odds")]')
            if len(fixed_odds_elem) == 0:
                win_price = None
            else:
                win_price = float(fixed_odds_elem[0]
                    .find_element(by=By.XPATH, value='.//span[@data-testid="price-button-odds"]')
                    .text)
            print(name, win_price)
        
        time.sleep(1)

        if depth < 100:
            f(depth+1)

    f(0)
    driver.close()

def analyse_data(market_data, odds, bonus_to_cash):
    if 'win' not in market_data or 'place' not in market_data:
        return {}

    win_odds = market_data['win']['markets']
    place_odds = market_data['place']['markets']

    evs = {}
    for name, bid_ask in win_odds.items():
        win_prob = 1 / (sum(bid_ask) / 2)
        place_prob = 1 / (sum(place_odds[name]) / 2)

        ev = win_prob * odds[name] + (place_prob - win_prob) * bonus_to_cash - 1
        evs[name] = ev
    return evs

path = '/usr/local/bin/chromedriver'

'''
try:
    horse_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198422516'
    horse_place_website = 'https://www.betfair.com.au/exchange/plus/horse-racing/market/1.198422517'

    lock = threading.Lock()

    win_thread = threading.Thread(target=scrape_odds_betfair, args=(horse_website, 'win', lock))
    place_thread = threading.Thread(target=scrape_odds_betfair, args=(horse_place_website, 'place', lock))

    win_thread.start()
    place_thread.start()

    odds = {
        'Dukono': 9.5,
        'Chattel Village': 34,
        'Hoy': 11,
        'Whisky Mcgonagall': 11,
        'Zakram': 34,
        'Zuffolo': 2.8,
        'Dante Star': 21,
        'Rievaulx Raver': 34,
        'Lakota Lady': 5,
        'Little Betty': 3.9,
    }
    bonus_to_cash = 0.7

    while True:
        evs = analyse_data(market_data, odds, bonus_to_cash)
        print(sorted(evs.items(), key=lambda x: -x[1]))
        time.sleep(10)

except Exception as e:
    print(e)

'''

ladbrokes = 'https://www.ladbrokes.com.au/racing/bendigo/afa34ed6-0ce1-42f4-858f-c6a7b74618da'
ladbrokes = 'https://www.ladbrokes.com.au/racing/capalaba/2df7bbaf-2b1d-438b-bab8-97e021cf8322'

scrape_odds_ladbrokes(ladbrokes)