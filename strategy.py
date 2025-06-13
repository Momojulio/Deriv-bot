import pandas as pd
import pandas_ta as ta


def is_bullish_engulfing(prev, curr):
    return (curr['close'] > curr['open']) and (prev['close'] < prev['open']) and                (curr['close'] >= prev['open']) and (curr['open'] <= prev['close'])


def is_bearish_engulfing(prev, curr):
    return (curr['close'] < curr['open']) and (prev['close'] > prev['open']) and                (curr['close'] <= prev['open']) and (curr['open'] >= prev['close'])


def is_hammer(candle):
    body = abs(candle['close'] - candle['open'])
    lower_shadow = candle['open'] - candle['low'] if candle['close'] >= candle['open'] else candle['close'] - candle['low']
    upper_shadow = candle['high'] - candle['close'] if candle['close'] >= candle['open'] else candle['high'] - candle['open']
    return lower_shadow > 2 * body and upper_shadow < body


def is_inverted_hammer(candle):
    body = abs(candle['close'] - candle['open'])
    upper_shadow = candle['high'] - candle['close'] if candle['close'] >= candle['open'] else candle['high'] - candle['open']
    lower_shadow = candle['open'] - candle['low'] if candle['close'] >= candle['open'] else candle['close'] - candle['low']
    return upper_shadow > 2 * body and lower_shadow < body


def compute_indicators(df: pd.DataFrame):
    df = df.copy()
    df['rsi'] = ta.rsi(df['close'], length=14)
    # supertrend returns columns with names like 'SUPERT_7_3.0' and 'SUPERTd_7_3.0'
    st = ta.supertrend(df['high'], df['low'], df['close'])
    df = pd.concat([df, st], axis=1)
    df[['adx', 'dmp', 'dmn']] = ta.adx(df['high'], df['low'], df['close'])
    return df


def decide(df: pd.DataFrame):
    """
    Expects df to contain the latest candles with columns: open, high, low, close
    Returns tuple (should_trade: bool, direction: str, pattern: str)
    """
    if len(df) < 3:
        return False, None, None
    df_ind = compute_indicators(df)
    last = df_ind.iloc[-1]
    prev = df_ind.iloc[-2]

    pattern = None
    direction = None

    if is_bullish_engulfing(prev, last) or is_hammer(last):
        pattern = 'BULLISH'
        direction = 'CALL'
    elif is_bearish_engulfing(prev, last) or is_inverted_hammer(last):
        pattern = 'BEARISH'
        direction = 'PUT'

    if pattern is None:
        return False, None, None

    # Filter conditions
    if last['adx'] < 20:
        return False, None, None
    if direction == 'CALL' and last['rsi'] > 70:
        return False, None, None
    if direction == 'PUT' and last['rsi'] < 30:
        return False, None, None

    # Supertrend filter
    st_dir_col = [c for c in df_ind.columns if c.startswith('SUPERTd')][-1]
    if direction == 'CALL' and last[st_dir_col] != 1:
        return False, None, None
    if direction == 'PUT' and last[st_dir_col] != -1:
        return False, None, None

    return True, direction, pattern
