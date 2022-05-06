import math
import signal
import threading
import time

from functools import partial
from tabulate import tabulate

from ev_functions import bonus_back_if_place_but_no_win, double_winnings_in_bonus, no_promotion, BET_SIZE
from scraper_manager import ScraperManager
from util import process_name

def get_betfair_odds(market_data, name):
    betfair_odds = {}
    for bookie_name, data in market_data.items():
        if 'betfair' in bookie_name:
            betfair_odds[bookie_name] = data['markets'].get(process_name(name))
    return betfair_odds

def analyse_data(market_data, bookie_promotion_types):
    global promo_index_to_name
    evs = {}
    for bookie_name, data in market_data.items():
        if 'betfair' in bookie_name:
            print(f'{bookie_name}: {data["matched"]}')
            continue

        evs[bookie_name] = []
        for runner_name, runner_odds in data.items():
            betfair_odds = get_betfair_odds(market_data, runner_name)
            for i, promo_func in enumerate(bookie_promotion_types.get(bookie_name, [])):
                ev = promo_func(runner_odds, betfair_odds)
                if ev is not None:
                    evs[bookie_name].append((runner_name, promo_index_to_name[i], runner_odds.back_odds, *ev))

    return evs

MAX_ROWS = 10

def loop():
    global window
    global MAX_ROWS
    global data_store
    global bookie_promos
    evs = analyse_data(data_store, bookie_promos)
    text_box_text = ''
    for key, val in evs.items():
        text_box_text += key + '\n'
        print_list = sorted(val, key=lambda x: math.inf if x[-1] is None else -x[-1])
        if len(print_list) > MAX_ROWS:
            print_list = print_list[:MAX_ROWS] + [('...', None, None, None)]
        else:
            print_list.extend([(None, None, None, None, None)] * (MAX_ROWS + 1 - len(print_list)))
        text_box_text += (tabulate(print_list, tablefmt='orgtbl',
            headers=['Name', 'Promo type', 'Bookie odds', 'EV', f'EV of {BET_SIZE} bet']))
    global text_box
    text_box.delete('1.0', tk.END)
    text_box.insert(tk.END, text_box_text)
    window.after(5000, loop)

def sigint_handler(signum, frame):
    print('HANDLE SIGINT!')
    global scraper_manager
    scraper_manager.stop_all()
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)



promo_index_to_name = [
    'NO PROMO',
    'BONUS BACK IF 2ND',
    'BONUS BACK IF 2ND-3RD',
    'BONUS BACK IF 2ND-4TH',
    'DOUBLE WINNINGS BONUS',
]

bookie_promos = {
    'bluebet': [no_promotion, partial(bonus_back_if_place_but_no_win, 2), partial(bonus_back_if_place_but_no_win, 3), partial(bonus_back_if_place_but_no_win, 4)],
    'ladbrokes': [no_promotion, partial(bonus_back_if_place_but_no_win, 2), partial(bonus_back_if_place_but_no_win, 3), partial(bonus_back_if_place_but_no_win, 4), double_winnings_in_bonus],
    'palmerbet': [no_promotion, partial(bonus_back_if_place_but_no_win, 3)],
    'pointsbet': [no_promotion, partial(bonus_back_if_place_but_no_win, 4)],
    'sportsbet': [no_promotion, partial(bonus_back_if_place_but_no_win, 2), partial(bonus_back_if_place_but_no_win, 3), partial(bonus_back_if_place_but_no_win, 4)],
    'tab': [no_promotion, partial(bonus_back_if_place_but_no_win, 2), partial(bonus_back_if_place_but_no_win, 3), partial(bonus_back_if_place_but_no_win, 4)],
}

data_store = {}
scraper_manager = ScraperManager(data_store)

import tkinter as tk

def on_create_thread_button_pressed():
    global url_entry
    global window
    url = url_entry.get()
    url_label = tk.Label(master=window, text=url)
    destroy_button = tk.Button(master=window, text='Stop')
    destroy_button.config(command=partial(on_destroy_thread_button_press, label=url_label, button=destroy_button))
    url_entry.delete(0, tk.END)
    url_label.pack()
    destroy_button.pack()
    scraper_manager.start(url)

def on_destroy_thread_button_press(label, button):
    scraper_manager.stop(label['text'])
    label.destroy()
    button.destroy()

window = tk.Tk()

text_box = tk.Text(master=window, height=50, width=100)
text_box.pack()

url_entry = tk.Entry(master=window, width=50)
url_entry.pack()

create_thread_button = tk.Button(master=window, command=on_create_thread_button_pressed, text='Scrape')
create_thread_button.pack()

loop()

def clean_up():
    global window
    global scraper_manager
    scraper_manager.stop_all()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", clean_up)

window.mainloop()