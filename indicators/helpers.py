def set_trend_direction(row):
    if row["↑"] and not row["↓"]:
        return "up"
    if not row["↑"] and row["↓"]:
        return "down"
    return None
