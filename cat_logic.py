from datetime import timedelta

from database import db, get_cat, now


def update_cat(user_id: int):
    """
    Показатели кота ухудшаются за каждый полный прошедший час.
    Неполный час сохраняется до следующего обновления.
    """

    cat = get_cat(user_id)

    if not cat:
        return None

    from datetime import datetime

    last_update = datetime.fromisoformat(cat["last_update"])
    elapsed = now() - last_update

    full_hours = int(elapsed.total_seconds() // 3600)

    if full_hours < 1:
        return cat

    hunger = max(0, cat["hunger"] - full_hours * 5)
    thirst = max(0, cat["thirst"] - full_hours * 7)
    toilet = max(0, cat["toilet"] - full_hours * 4)
    affection = max(0, cat["affection"] - full_hours * 2)

    new_last_update = last_update + timedelta(hours=full_hours)

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
        new_last_update.isoformat(),
        user_id
    ))

    db.commit()

    return get_cat(user_id)


def change_stat(user_id: int, stat: str, amount: int):
    cat = update_cat(user_id)

    if not cat:
        return None

    new_value = min(100, cat[stat] + amount)

    db.execute(
        f"UPDATE cats SET {stat} = ? WHERE user_id = ?",
        (new_value, user_id)
    )

    db.commit()

    return get_cat(user_id)