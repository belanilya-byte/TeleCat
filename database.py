import sqlite3
from datetime import datetime, timezone

from config import DATABASE_PATH


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

db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    owner_name TEXT,
    language TEXT,
    last_active TEXT
)
""")

# Add owner data to existing databases
columns = {
    row["name"]
    for row in db.execute("PRAGMA table_info(cats)").fetchall()
}

if "owner_name" not in columns:
    db.execute(
        "ALTER TABLE cats ADD COLUMN owner_name TEXT"
    )

if "language" not in columns:
    db.execute(
        "ALTER TABLE cats ADD COLUMN language TEXT"
    )

if "username" not in columns:
    db.execute(
        "ALTER TABLE cats ADD COLUMN username TEXT"
    )

if "last_active" not in columns:
    db.execute(
        "ALTER TABLE cats ADD COLUMN last_active TEXT"
    )

if "onboarding_state" not in columns:
    db.execute(
        "ALTER TABLE cats ADD COLUMN onboarding_state TEXT"
    )

db.execute("""
INSERT OR IGNORE INTO users (
    user_id,
    username,
    owner_name,
    language,
    last_active
)
SELECT
    user_id,
    username,
    owner_name,
    language,
    last_active
FROM cats
""")

db.commit()


def now():
    return datetime.now(timezone.utc)


def get_cat(user_id: int):
    return db.execute(
        "SELECT * FROM cats WHERE user_id = ?",
        (user_id,)
    ).fetchone()


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


def get_all_cats():
    return db.execute("""
        SELECT
            users.user_id,
            users.username,
            users.owner_name,
            users.language,
            users.last_active,
            cats.name AS cat_name
        FROM users
        JOIN cats
            ON users.user_id = cats.user_id
        ORDER BY users.last_active DESC
    """).fetchall()


def update_user_info(
    user_id: int,
    username: str | None,
    language: str | None
):
    timestamp = now().isoformat()

    if language not in ("ru", "en", "he"):
        language = "en"

    db.execute("""
        INSERT INTO users (
            user_id,
            username,
            language,
            last_active
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            language = excluded.language,
            last_active = excluded.last_active
    """, (
        user_id,
        username,
        language,
        timestamp
    ))

    db.commit()


def set_onboarding_state(user_id: int, state: str):
    db.execute(
        "UPDATE cats SET onboarding_state = ? WHERE user_id = ?",
        (state, user_id)
    )
    db.commit()


def set_owner_name(user_id: int, owner_name: str):
    db.execute(
        "UPDATE users SET owner_name = ? WHERE user_id = ?",
        (owner_name, user_id)
    )
    db.commit()


def set_cat_name(user_id: int, cat_name: str):
    db.execute(
        "UPDATE cats SET name = ? WHERE user_id = ?",
        (cat_name, user_id)
    )
    db.commit()


def set_language(user_id: int, language: str):
    db.execute(
        "UPDATE users SET language = ? WHERE user_id = ?",
        (language, user_id)
    )
    db.commit()


def get_user(user_id: int):
    return db.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()