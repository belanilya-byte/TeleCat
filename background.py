import asyncio
import random

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

from database import db, get_cat, set_onboarding_state
from cat_logic import update_cat
from ui import cat_keyboard, language_keyboard
from localization import get_text


async def start_onboarding(bot: Bot, user_id: int):
    delay = random.randint(0, 3600)
    await asyncio.sleep(delay)

    cat = get_cat(user_id)

    if not cat or cat["onboarding_state"] is not None:
        return

    user = db.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    language = user["language"] if user else None

    try:
        if language is None:
            await bot.send_message(
                user_id,
                "Language / Язык / שפה",
                reply_markup=language_keyboard()
            )
            return

        await bot.send_message(
            user_id,
            get_text(language, "ask_owner_name")
        )

        set_onboarding_state(user_id, "waiting_owner_name")

    except TelegramForbiddenError:
        return


async def schedule_onboarding(bot: Bot):
    users = db.execute(
        """
        SELECT user_id
        FROM cats
        WHERE onboarding_state IS NULL
        """
    ).fetchall()

    for user in users:
        asyncio.create_task(
            start_onboarding(bot, user["user_id"])
        )


async def send_background_message(
    bot: Bot,
    user_id: int,
    language: str,
    key: str
):
    try:
        replies = get_text(language, key)

        await bot.send_message(
            user_id,
            random.choice(replies),
            reply_markup=cat_keyboard(language)
        )

    except TelegramForbiddenError:
        return


async def cat_background_loop(bot: Bot):
    while True:
        await asyncio.sleep(60)

        cats = db.execute(
            """
            SELECT
                cats.user_id,
                users.language
            FROM cats
            JOIN users
                ON cats.user_id = users.user_id
            """
        ).fetchall()

        for row in cats:
            user_id = row["user_id"]
            language = row["language"] or "en"

            cat = update_cat(user_id)

            if not cat:
                continue

            if cat["hunger"] <= 25:
                if random.random() < 0.15:
                    await send_background_message(
                        bot,
                        user_id,
                        language,
                        "background_hungry"
                    )

            elif cat["thirst"] <= 25:
                if random.random() < 0.15:
                    await send_background_message(
                        bot,
                        user_id,
                        language,
                        "background_thirsty"
                    )

            elif cat["toilet"] <= 20:
                if random.random() < 0.15:
                    await send_background_message(
                        bot,
                        user_id,
                        language,
                        "background_toilet"
                    )

            elif cat["affection"] <= 25:
                if random.random() < 0.15:
                    await send_background_message(
                        bot,
                        user_id,
                        language,
                        "background_lonely"
                    )

            elif random.random() < 0.01:
                await send_background_message(
                    bot,
                    user_id,
                    language,
                    "background_random"
                )