from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


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


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Русский",
                    callback_data="lang_ru"
                ),
                InlineKeyboardButton(
                    text="English",
                    callback_data="lang_en"
                ),
                InlineKeyboardButton(
                    text="עברית",
                    callback_data="lang_he"
                ),
            ]
        ]
    )