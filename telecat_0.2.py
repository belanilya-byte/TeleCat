import asyncio

from aiogram import Bot

from config import BOT_TOKEN
from handlers import dp
from background import cat_background_loop, schedule_onboarding


bot = Bot(token=BOT_TOKEN)


async def main():
    await schedule_onboarding(bot)

    asyncio.create_task(
        cat_background_loop(bot)
    )

    print("TeleCat Mk.0.2 is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())