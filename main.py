import math
import signal
from functools import partial

from tabulate import tabulate

from data_store import DataStore
from entities.bookie_type import BookieType
from entities.promo_types import BET_SIZE, NoPromo, \
    BonusBackIfPlaceButNoWin, BonusBackEqualToWinnings
from scraper_manager import ScraperManager


def analyse_data(market_data, bookie_promotion_types):
    global promo_index_to_name
    global promos
    evs = {}
    for bookie_type, data in market_data.items():
        if bookie_type in BookieType.BETFAIR:
            continue

        evs[bookie_type] = []
        for runner_name, runner_odds in data.items():
            for promo_ind in bookie_promotion_types.get(bookie_type, []):
                evinfo = promos[promo_ind].get_ev_info(bookie_type, runner_name)
                if evinfo is not None:
                    ev = (evinfo.ev_per_dollar,
                          *evinfo.ev_per_dollar_bounds), evinfo.ev_of_bet
                    evs[bookie_type].append((runner_name,
                                             promo_index_to_name[promo_ind],
                                             runner_odds.back_odds, *ev))

    return evs


def to_str(x, tuple_to_str=False):
    if type(x) is str:
        return x[:MAX_STR_LEN]
    if type(x) is float:
        return f'{x:.2f}'
    if type(x) is tuple:
        tuple_of_strs = tuple(to_str(i, True) for i in x)
        if tuple_to_str:
            return f'({", ".join(tuple_of_strs)})'
        return tuple_of_strs
    return None


MAX_ROWS = 8
MAX_STR_LEN = 25
filters = [lambda x: x[2] < 12]


def two_columnify(tables):
    two_col_list = []
    for i, table in enumerate(tables):
        table_list = table.split('\n')
        if i % 2 == 0:
            two_col_list.extend([''] * len(table_list))
        for j, line in enumerate(reversed(table_list)):
            two_col_list[-j - 1] += line
    return '\n'.join(two_col_list)


def loop():
    global window
    global MAX_ROWS
    global data_store
    global bookie_promos
    global matched_box
    evs = analyse_data(data_store.data_store, bookie_promos)
    tables = []
    for key, val in evs.items():
        print_list = sorted(val,
                            key=lambda x: math.inf if x[-1] is None else -x[-1])
        for f in filters:
            print_list = filter(f, print_list)
        print_list = list(map(to_str, print_list))
        if len(print_list) > MAX_ROWS:
            print_list = print_list[:MAX_ROWS] + [('...', None, None, None)]
        else:
            print_list.extend([(None, None, None, None, None)] * (
                    MAX_ROWS + 1 - len(print_list)))
        tables.append((tabulate(print_list, tablefmt='orgtbl',
                                headers=[f'{key} Name', 'Promo Type',
                                         'Bet Odds', 'EV/$1',
                                         f'EV/${BET_SIZE}'])))
    global text_box
    text_box.delete('1.0', tk.END)
    text_box.insert(tk.END, two_columnify(tables))

    matched_box_text = ''
    for market in ['betfair_win', 'betfair_2_place', 'betfair_3_place',
                   'betfair_4_place']:
        if market in data_store.data_store and 'matched' in \
                data_store.data_store[market]:
            matched_box_text += f'{market}: {data_store.data_store[market]["matched"]}\n'
    matched_box.delete('1.0', tk.END)
    matched_box.insert(tk.END, matched_box_text)

    window.after(5000, loop)


def sigint_handler(signum, frame):
    global scraper_manager
    scraper_manager.stop_all()
    exit(0)


signal.signal(signal.SIGINT, sigint_handler)

data_store = DataStore()
scraper_manager = ScraperManager(data_store)

BONUS_TO_CASH_RATIO = 0.75

promo_index_to_name = [
    'NO PROMO',
    'BONUS IF 2',
    'BONUS IF 2-3',
    'BONUS IF 2-4',
    'DOUBLE BONUS',
]

promos = [
    NoPromo(data_store, bet_limit=50),
    BonusBackIfPlaceButNoWin(data_store, 2,
                             bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                             bet_limit=50),
    BonusBackIfPlaceButNoWin(data_store, 3,
                             bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                             bet_limit=50),
    BonusBackIfPlaceButNoWin(data_store, 4,
                             bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                             bet_limit=50),
    BonusBackEqualToWinnings(data_store,
                             bonus_to_cash_ratio=BONUS_TO_CASH_RATIO,
                             winnings_limit=50),
]

bookie_promos = {
    BookieType.BET365: [0, 2],
    BookieType.BETDELUXE: [0, 2],
    BookieType.BLUEBET: [0, 2],
    BookieType.LADBROKES: [0, 2, 4],
    BookieType.PALMERBET: [0, 2],
    BookieType.POINTSBET: [0, 2, 3],
    BookieType.SPORTSBET: [0, 2],
    BookieType.TAB: [0, 2, 3],
}

import tkinter as tk


def on_create_thread_button_pressed(*args):
    global url_entry
    global window
    url = url_entry.get()
    destroy_button = tk.Button(master=window, text=f'{url} Stop')
    destroy_button.config(
        command=partial(on_destroy_thread_button_press, button=destroy_button))
    url_entry.delete(0, tk.END)
    destroy_button.pack()
    scraper_manager.start(url)


def on_destroy_thread_button_press(button):
    scraper_manager.stop(button['text'][:-5])
    button.destroy()


window = tk.Tk()

matched_box = tk.Text(master=window, height=2, width=20)
matched_box.pack()

text_box = tk.Text(master=window, height=35, width=166,
                   font=('courier new', 16))
text_box.pack()

url_entry = tk.Entry(master=window, width=50)
url_entry.focus_set()
url_entry.pack()

window.bind('<Return>', on_create_thread_button_pressed)
create_thread_button = tk.Button(master=window,
                                 command=on_create_thread_button_pressed,
                                 text='Scrape')
create_thread_button.pack()

loop()


def clean_up():
    global window
    global scraper_manager
    scraper_manager.stop_all()
    window.destroy()


window.protocol("WM_DELETE_WINDOW", clean_up)

window.mainloop()
