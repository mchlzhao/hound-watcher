from entities.bookie_type import BookieType
from util import process_name


class DataStore:
    def __init__(self):
        self.data_store = {}

    def update_data(self, bookie_type: BookieType, data):
        if bookie_type.is_betfair():
            data['markets'] = {process_name(k): v for k, v in
                               data['markets'].items()}
        else:
            data = {process_name(k): v for k, v in data.items()}
        self.data_store[bookie_type] = data

    def clear_data(self, bookie_type):
        self.data_store.pop(bookie_type, None)

    def get_odds(self, bookie_type: BookieType, runner_name: str):
        bookie_data = self.data_store.get(bookie_type)
        if bookie_data is None:
            return None
        if bookie_type.is_betfair():
            bookie_data = bookie_data['markets']
        return bookie_data.get(runner_name)
