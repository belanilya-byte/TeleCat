from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from localization import get_text


def cat_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, "button_feed"),
                    callback_data="feed"
                ),
                InlineKeyboardButton(
                    text=get_text(language, "button_water"),
                    callback_data="water"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, "button_toilet"),
                    callback_data="toilet"
                ),
                InlineKeyboardButton(
                    text=get_text(language, "button_pet"),
                    callback_data="pet"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, "button_status"),
                    callback_data="status"
                )
            ]
        ]
    )


def status_text(cat, language: str):
    return (
        f"🐱 {cat['name']}\n\n"
        f"🥩 {get_text(language, 'status_hunger')}: {cat['hunger']}/100\n"
        f"💧 {get_text(language, 'status_water')}: {cat['thirst']}/100\n"
        f"🧹 {get_text(language, 'status_toilet')}: {cat['toilet']}/100\n"
        f"❤️ {get_text(language, 'status_affection')}: {cat['affection']}/100"
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