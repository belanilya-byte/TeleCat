import random

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from database import (
    db,
    get_cat,
    create_cat,
    get_all_cats,
    update_user_info,
    set_language,
    set_onboarding_state,
    set_owner_name,
    set_cat_name,
    get_user,
)
from cat_logic import update_cat, change_stat
from ui import cat_keyboard, status_text
from localization import get_text


dp = Dispatcher()


def get_user_language(user_id: int):
    user = get_user(user_id)

    if not user or not user["language"]:
        return "en"

    return user["language"]


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

    language = get_user_language(user_id)

    if is_new:
        await message.answer(
            get_text(language, "start_new"),
            reply_markup=cat_keyboard(language)
        )
        return

    update_cat(user_id)

    await message.answer(
        get_text(language, "start_existing"),
        reply_markup=cat_keyboard(language)
    )


@dp.callback_query(F.data == "feed")
async def feed_cat(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = get_user_language(user_id)

    change_stat(user_id, "hunger", 30)

    replies = get_text(
        language,
        "feed_replies"
    )

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard(language)
    )

    await callback.answer()


@dp.callback_query(F.data == "water")
async def water_cat(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = get_user_language(user_id)

    change_stat(user_id, "thirst", 40)

    replies = get_text(
        language,
        "water_replies"
    )

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard(language)
    )

    await callback.answer()


@dp.callback_query(F.data == "toilet")
async def clean_toilet(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = get_user_language(user_id)

    change_stat(user_id, "toilet", 100)

    replies = get_text(
        language,
        "toilet_replies"
    )

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard(language)
    )

    await callback.answer()


@dp.callback_query(F.data == "pet")
async def pet_cat(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = get_user_language(user_id)

    change_stat(user_id, "affection", 20)

    replies = get_text(
        language,
        "pet_replies"
    )

    await callback.message.answer(
        random.choice(replies),
        reply_markup=cat_keyboard(language)
    )

    await callback.answer()


@dp.callback_query(F.data == "status")
async def show_status(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = get_user_language(user_id)

    cat = update_cat(user_id)

    await callback.message.answer(
        status_text(cat, language),
        reply_markup=cat_keyboard(language)
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

    update_user_info(
        user_id,
        message.from_user.username,
        message.from_user.language_code
    )

    cat = get_cat(user_id)

    if not cat:
        return

    state = cat["onboarding_state"]
    language = get_user_language(user_id)

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