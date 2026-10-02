import asyncio
import os
import random
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "telecat.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found")


# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect(DATABASE_PATH)
db.row_factory = sqlite3.Row

db.execute("""
CREATE TABLE IF NOT EXISTS cats (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'Кот',
    hunger INTEGER NOT NULL DEFAULT 80,
    thirst INTEGER NOT NULL DEFAULT 80,
    toilet INTEGER NOT NULL DEFAULT 80,
    affection INTEGER NOT NULL DEFAULT 50,
    created_at TEXT NOT NULL,
    last_update TEXT NOT NULL
)
""")

db.commit()


def now():
    return datetime.now(timezone.utc)


def get_cat(user_id: int):
    cat = db.execute(
        "SELECT * FROM cats WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    return cat


def create_cat(user_id: int):
    timestamp = now().isoformat()

    db.execute("""
        INSERT INTO cats (
            user_id,
            created_at,
            last_update
        )
        VALUES (?, ?, ?)
    """, (user_id, timestamp, timestamp))

    db.commit()

    return get_cat(user_id)


# ============================================================
# CAT LOGIC
# ============================================================

def update_cat(user_id: int):
    """
    Показатели кота ухудшаются со временем.
    Пока формулы максимально простые.
    """

    cat = get_cat(user_id)

    if not cat:
        return None

    last_update = datetime.fromisoformat(cat["last_update"])

    elapsed = now() - last_update
    hours = elapsed.total_seconds() / 3600

    if hours < 0.1:
        return cat

    hunger = max(0, cat["hunger"] - int(hours * 5))
    thirst = max(0, cat["thirst"] - int(hours * 7))
    toilet = max(0, cat["toilet"] - int(hours * 4))
    affection = max(0, cat["affection"] - int(hours * 2))

    db.execute("""
        UPDATE cats
        SET hunger = ?,
            thirst = ?,
            toilet = ?,
            affection = ?,
            last_update = ?
        WHERE user_id = ?
    """, (
        hunger,
        thirst,
        toilet,
        affection,
        now().isoformat(),
        user_id
    ))

    db.commit()

    return get_cat(user_id)


def change_stat(user_id: int, stat: str, amount: int):
    cat = update_cat(user_id)

    new_value = min(100, cat[stat] + amount)

    db.execute(
        f"UPDATE cats SET {stat} = ? WHERE user_id = ?",
        (new_value, user_id)
    )

    db.commit()


# ============================================================
# UI
# ============================================================

def cat_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🥩 Покормить",
                    callback_data="feed"
                ),
                InlineKeyboardButton(
                    text="💧 Вода",
                    callback_data="water"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🧹 Убрать лоток",
                    callback_data="toilet"
                ),
                InlineKeyboardButton(
                    text="🖐 Погладить",
                    callback_data="pet"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Состояние",
                    callback_data="status"
                )
            ]
        ]
    )


def status_text(cat):
    return (
        f"🐱 {cat['name']}\n\n"
        f"🥩 Сытость: {cat['hunger']}/100\n"
        f"💧 Вода: {cat['thirst']}/100\n"
        f"🧹 Лоток: {cat['toilet']}/100\n"
        f"❤️ Общение: {cat['affection']}/100"
    )


# ============================================================
# BOT
# ============================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/users")
async def users_command(message: Message):
    if message.from_user.id != 350922718:
        return

    count = db.execute(
        "SELECT COUNT(*) FROM cats"
    ).fetchone()[0]

    await message.answer(
    f"🐱 Cats: {count}\n"
    f"👤 Your ID: {message.from_user.id}"
)

@dp.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id

    cat = get_cat(user_id)

    if not cat:
        cat = create_cat(user_id)

        await message.answer(
            "🥚\n\n"
            "*тресь*\n\n"
            "Из яйца вылезло что-то маленькое.\n\n"
            "Оно посмотрело на тебя.\n\n"
            "Мяу.",
            reply_markup=cat_keyboard()
        )

        return

    cat = update_cat(user_id)

    await message.answer(
        "Мяу.",
        reply_markup=cat_keyboard()
    )


# ============================================================
# ACTIONS
# ============================================================

@dp.callback_query(F.data == "feed")
async def feed_cat(callback: CallbackQuery):

    change_stat(callback.from_user.id, "hunger", 30)

    replies = [
        "*жрёт*",
        "Ещё.",
        "Нормально.",
        "*утащил кусок куда-то*",
        "Это всё?",
    ]

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "water")
async def water_cat(callback: CallbackQuery):

    change_stat(callback.from_user.id, "thirst", 40)

    replies = [
        "*пьёт*",
        "*потрогал воду лапой*",
        "Нормальная.",
        "*пьёт из самого дальнего края миски*",
    ]

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "toilet")
async def clean_toilet(callback: CallbackQuery):

    change_stat(callback.from_user.id, "toilet", 100)

    replies = [
        "*немедленно полез в чистый лоток*",
        "Наконец.",
        "*проверил качество уборки*",
        "Мяу.",
    ]

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "pet")
async def pet_cat(callback: CallbackQuery):

    change_stat(callback.from_user.id, "affection", 20)

    replies = [
        "*мурчит*",
        "*подставил голову*",
        "*кусь*",
        "Ещё.",
        "*потёрся мордой о руку*",
        "*через три секунды передумал и ушёл*",
    ]

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard()
    )

    await callback.answer()


@dp.callback_query(F.data == "status")
async def show_status(callback: CallbackQuery):

    cat = update_cat(callback.from_user.id)

    await callback.message.answer(
        status_text(cat),
        reply_markup=cat_keyboard()
    )

    await callback.answer()


# ============================================================
# RANDOM CAT REQUESTS
# ============================================================

async def cat_background_loop():

    while True:

        await asyncio.sleep(60)

        cats = db.execute(
            "SELECT user_id FROM cats"
        ).fetchall()

        for row in cats:

            user_id = row["user_id"]
            cat = update_cat(user_id)

            if cat["hunger"] <= 25:

                if random.random() < 0.15:

                    try:
                        await bot.send_message(
                            user_id,
                            random.choice([
                                "Миска пустая.",
                                "Я проверил. Еды нет.",
                                "Ты забыл про кота.",
                                "Мяу.\n\nМяу.\n\nМЯУ.",
                            ]),
                            reply_markup=cat_keyboard()
                        )

                    except Exception:
                        pass

            elif cat["thirst"] <= 25:

                if random.random() < 0.15:

                    try:
                        await bot.send_message(
                            user_id,
                            random.choice([
                                "Воды.",
                                "В миске какая-то фигня. Налей новую.",
                                "*сидит возле миски и смотрит на тебя*",
                            ]),
                            reply_markup=cat_keyboard()
                        )

                    except Exception:
                        pass

            elif cat["toilet"] <= 20:

                if random.random() < 0.15:

                    try:
                        await bot.send_message(
                            user_id,
                            random.choice([
                                "Лоток.",
                                "Убери.",
                                "*демонстративно скребёт пол рядом с лотком*",
                            ]),
                            reply_markup=cat_keyboard()
                        )

                    except Exception:
                        pass


# ============================================================
# RUN
# ============================================================

async def main():

    asyncio.create_task(cat_background_loop())

    print("Telecat Mk.0.1 is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())