from util import process_name


class DataStore:
    def __init__(self):
        self.data_store = {}

    def update_data(self, bookie_name, data):
        if 'betfair' in bookie_name:
            data['markets'] = {process_name(k): v for k, v in
                               data['markets'].items()}
        else:
            data = {process_name(k): v for k, v in data.items()}
        self.data_store[bookie_name] = data

    def clear_data(self, bookie_name):
        self.data_store.pop(bookie_name, None)

    def get_odds(self, bookie_name, runner_name):
        bookie_data = self.data_store.get(bookie_name)
        if bookie_data is None:
            return None
        if 'betfair' in bookie_name:
            bookie_data = bookie_data['markets']
        return bookie_data.get(runner_name)
