import asyncio
from config import TELEGRAM_TOKEN
from settings_manager import Settings
from telegram_bot import run_telegram
from deriv_ws import DerivWS


async def main():
    settings = Settings.load()

    # function to send message from DerivWS to Telegram
    queue = asyncio.Queue()

    async def notify(message: str):
        await queue.put(message)

    deriv = DerivWS(settings, notify)

    async def bridge():
        while True:
            msg = await queue.get()
            # Here we reuse telegram application to send message
            # Lazy import inside to avoid circular
            from telegram import Bot
            bot = Bot(TELEGRAM_TOKEN)
            from config import TELEGRAM_USER_ID
            await bot.send_message(TELEGRAM_USER_ID, msg)

    await asyncio.gather(
        deriv.run(),
        run_telegram(settings, notify),
        bridge()
    )

if __name__ == "__main__":
    asyncio.run(main())
