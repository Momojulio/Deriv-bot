import csv
import os
from datetime import datetime
from typing import Dict

from config import LOG_FILE

header = [
    "timestamp",
    "asset",
    "timeframe",
    "pattern",
    "direction",
    "entry_price",
    "result",
    "payout"
]


def _ensure_file_exists():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def log_trade(entry: Dict):
    _ensure_file_exists()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([entry.get(k, '') for k in header])


def summary(limit: int = 20):
    _ensure_file_exists()
    rows = []
    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    last_rows = rows[-limit:]
    wins = sum(1 for r in last_rows if r['result'] == 'WIN')
    losses = sum(1 for r in last_rows if r['result'] == 'LOSS')
    return wins, losses, last_rows
