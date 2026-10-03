import random

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from database import (db, get_cat, create_cat, get_all_cats, update_user_info, set_language, set_onboarding_state, set_owner_name, set_cat_name)
from cat_logic import update_cat, change_stat
from ui import cat_keyboard, status_text
from localization import get_text


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
    is_new = cat is None

    if is_new:
        cat = create_cat(user_id)

    update_user_info(
        user_id,
        message.from_user.username,
        message.from_user.language_code
    )

    if is_new:
        await message.answer(
            "🥚\n\n"
            "*тресь*\n\n"
            "Из яйца вылезло что-то маленькое.\n\n"
            "Оно посмотрело на тебя.\n\n"
            "Мяу.",
            reply_markup=cat_keyboard()
        )
        return

    update_cat(user_id)

    await message.answer(
        "Мяу.",
        reply_markup=cat_keyboard()
    )


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


@dp.message(F.text == "/usersinfo")
async def users_info_command(message: Message):
    if message.from_user.id != 350922718:
        return

    users = get_all_cats()

    lines = [f"👥 Users: {len(users)}\n"]

    for user in users:
        user_id = user["user_id"]
        username = user["username"]
        owner_name = user["owner_name"] or "Unknown"
        cat_name = user["cat_name"]

        if username:
            profile = f"https://t.me/{username}"
        else:
            profile = "No public username"

        lines.append(
            f"👤 {owner_name}\n"
            f"🐱 {cat_name}\n"
            f"🆔 {user_id}\n"
            f"🔗 {profile}\n"
        )

    await message.answer("\n".join(lines))


@dp.message(F.text)
async def onboarding_message(message: Message):
    user_id = message.from_user.id
    update_user_info(user_id, message.from_user.username, message.from_user.language_code)
    cat = get_cat(user_id)

    if not cat:
        return

    state = cat["onboarding_state"]
    language = cat["language"] or "en"

    if state == "waiting_owner_name":
        owner_name = message.text.strip()

        set_owner_name(user_id, owner_name)
        set_onboarding_state(user_id, "waiting_cat_name")

        await message.answer(
            get_text(
                language,
                "ask_cat_name",
                owner_name=owner_name
            )
        )
        return

    if state == "waiting_cat_name":
        cat_name = message.text.strip()

        set_cat_name(user_id, cat_name)
        set_onboarding_state(user_id, "complete")

        await message.answer(
            get_text(
                language,
                "onboarding_complete",
                cat_name=cat_name
            )
        )
        return

    if state == "complete":
        replies = get_text(
            language,
            "idle_replies",
            cat_name=cat["name"]
        )

        await message.answer(
            random.choice(replies)
        )


@dp.callback_query(F.data.in_({"lang_ru", "lang_en", "lang_he"}))
async def choose_language(callback: CallbackQuery):
    language = callback.data.replace("lang_", "")
    user_id = callback.from_user.id

    set_language(user_id, language)
    set_onboarding_state(user_id, "waiting_owner_name")

    await callback.message.answer(
        get_text(language, "ask_owner_name")
    )

    await callback.answer()