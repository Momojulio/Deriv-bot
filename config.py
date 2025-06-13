import os

# ================== CONFIGURATION ==================
# These variables are populated from Render 'Environment' tab.
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID: int = int(os.getenv("TELEGRAM_USER_ID", "123456789"))

DERIV_TOKEN: str = os.getenv("DERIV_TOKEN", "YOUR_DERIV_API_TOKEN")
DERIV_APP_ID: str = os.getenv("DERIV_APP_ID", "1089")  # default public app_id

SETTINGS_FILE = "settings.json"
LOG_FILE = "trade_log.csv"
