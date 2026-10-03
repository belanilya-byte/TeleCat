from database import db, get_cat, now


def update_cat(user_id: int):
    """
    Показатели кота ухудшаются со временем.
    """

    cat = get_cat(user_id)

    if not cat:
        return None

    from datetime import datetime

    last_update = datetime.fromisoformat(cat["last_update"])
    elapsed = now() - last_update
    hours = elapsed.total_seconds() / 3600

    hunger_decay = int(hours * 5)
    thirst_decay = int(hours * 7)
    toilet_decay = int(hours * 4)
    affection_decay = int(hours * 2)

    if not any((
        hunger_decay,
        thirst_decay,
        toilet_decay,
        affection_decay
    )):
        return cat

    hunger = max(0, cat["hunger"] - hunger_decay)
    thirst = max(0, cat["thirst"] - thirst_decay)
    toilet = max(0, cat["toilet"] - toilet_decay)
    affection = max(0, cat["affection"] - affection_decay)

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

    if not cat:
        return None

    new_value = min(100, cat[stat] + amount)

    db.execute(
        f"UPDATE cats SET {stat} = ? WHERE user_id = ?",
        (new_value, user_id)
    )

    db.commit()

    return get_cat(user_id)