# Deriv Binary Options Bot (Render-ready)

**Created on 2025-06-13**

## 🌟 Features

- Auto-trades on Deriv synthetic indices 24/7  
- Uses reliable candlestick patterns (Engulfing, Hammer, Inverted Hammer)  
- Adds Supertrend, RSI and ADX filters for higher win‑rate  
- No martingale – fixed stake per trade  
- Full remote control via Telegram commands  
- Trade journal saved locally + `/journal` overview in Telegram  

## 🏗 Project tree

```
deriv_bot/
├── main.py
├── config.py
├── telegram_bot.py
├── deriv_ws.py
├── strategy.py
├── settings_manager.py
├── logger.py
├── settings.json
└── requirements.txt
```

## 🚀 Deploy on Render (free tier)

1. **Create a new Web Service**  
   - Environment → Python 3.11  
   - Start command → `python main.py`

2. **Environment variables**  
   | Key | Value |
   |-----|-------|
   | `TELEGRAM_TOKEN` | Your bot token |
   | `TELEGRAM_USER_ID` | Your numeric Telegram ID |
   | `DERIV_TOKEN` | Your Deriv API token |
   | `DERIV_APP_ID` | 1089 or your own |

3. **Build commands**  
   ```
   pip install -r requirements.txt
   ```

## 📟 Telegram commands

| Command | Description |
|---------|-------------|
| `/set_demo` | Utiliser compte démo |
| `/set_real` | Utiliser compte réel |
| `/set_timeframe 1m/5m` | Choisir timeframe |
| `/set_amount <N>` | Modifier le stake (USD) |
| `/set_mode auto/manual` | Activer/désactiver trading auto |
| `/journal` | Affiche les 20 derniers trades |

## ⚠️ Notes

- Render free dyno dort après 15 min d’inactivité web. Le WebSocket ping (30 s) garde la connexion vivante.  
- Toujours commencer en **démo** pour valider la stratégie avant réel.
