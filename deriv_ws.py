import asyncio
import json
import websockets
from datetime import datetime, timezone
from typing import Callable, List, Dict

from config import DERIV_TOKEN, DERIV_APP_ID
from strategy import decide
from logger import log_trade
from settings_manager import Settings

WS_ENDPOINT = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"


class DerivWS:
    def __init__(self, settings: Settings, notify: Callable[[str], None]):
        self.settings = settings
        self._notify = notify
        self._socket = None
        self._candles: Dict[str, List[Dict]] = {}

    async def _send(self, msg):
        await self._socket.send(json.dumps(msg))

    async def _authorize(self):
        await self._send({'authorize': DERIV_TOKEN})

    async def _subscribe_ticks(self, symbol):
        await self._send({'ticks': symbol, 'subscribe': 1})

    async def _buy_contract(self, symbol, direction):
        amount = self.settings.trade_amount
        contract_type = 'CALL' if direction == 'CALL' else 'PUT'
        duration = 60 if self.settings.timeframe == '1m' else 300
        buy_request = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": duration,
                "duration_unit": "s",
                "symbol": symbol
            }
        }
        await self._send(buy_request)

    def _update_candles(self, symbol, tick):
        timeframe = 60 if self.settings.timeframe == '1m' else 300
        ts = datetime.fromtimestamp(tick['epoch'], tz=timezone.utc)
        candle_key = ts.replace(second=0, microsecond=0)
        if symbol not in self._candles:
            self._candles[symbol] = []
        if self._candles[symbol] and self._candles[symbol][-1]['start'] == candle_key:
            candle = self._candles[symbol][-1]
            candle['high'] = max(candle['high'], tick['quote'])
            candle['low'] = min(candle['low'], tick['quote'])
            candle['close'] = tick['quote']
        else:
            # new candle
            candle = {
                'start': candle_key,
                'open': tick['quote'],
                'high': tick['quote'],
                'low': tick['quote'],
                'close': tick['quote']
            }
            self._candles[symbol].append(candle)
            # keep last 100 candles
            if len(self._candles[symbol]) > 100:
                self._candles[symbol] = self._candles[symbol][-100:]

    async def run(self):
        while True:
            try:
                async with websockets.connect(WS_ENDPOINT, ping_interval=30, ping_timeout=10) as ws:
                    self._socket = ws
                    await self._authorize()
                    await self._subscribe_ticks(self.settings.active_asset)

                    async for message in ws:
                        data = json.loads(message)

                        if 'tick' in data:
                            tick = data['tick']
                            self._update_candles(tick['symbol'], tick)
                            candles = self._candles[tick['symbol']]
                            df_data = [{
                                'open': c['open'],
                                'high': c['high'],
                                'low': c['low'],
                                'close': c['close']
                            } for c in candles]
                            import pandas as pd
                            df = pd.DataFrame(df_data)
                            should_trade, direction, pattern = decide(df)
                            if should_trade and self.settings.mode == 'auto':
                                await self._buy_contract(tick['symbol'], direction)
                                msg = f"📈 Trade placed: {direction} on {tick['symbol']} using pattern {pattern}"
                                self._notify(msg)
                        elif 'buy' in data:
                            # handle buy response
                            pass
            except Exception as e:
                self._notify(f"Deriv WS error: {e}")
                await asyncio.sleep(5)
