import json
import os
from config import SETTINGS_FILE


class Settings:
    def __init__(self, data):
        self._data = data

    @property
    def account_mode(self):
        return self._data.get('account_mode', 'demo')

    @property
    def timeframe(self):
        return self._data.get('timeframe', '1m')

    @property
    def trade_amount(self):
        return self._data.get('trade_amount', 1.0)

    @property
    def mode(self):
        return self._data.get('mode', 'auto')

    @mode.setter
    def mode(self, value):
        self._data['mode'] = value

    @property
    def active_asset(self):
        return self._data.get('active_asset', 'R_50')

    def save(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self._data, f, indent=4)

    @classmethod
    def load(cls):
        if not os.path.exists(SETTINGS_FILE):
            return cls({})
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        return cls(data)
