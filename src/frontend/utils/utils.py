from datetime import datetime, timezone

def format_time_ago(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "только что"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин. назад"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ч. назад"
    elif seconds < 2592000:
        days = seconds // 86400
        return f"{days} дн. назад"
    else:
        months = seconds // 2592000
        return f"{months} мес. назад"