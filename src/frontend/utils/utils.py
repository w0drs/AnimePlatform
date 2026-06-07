from datetime import datetime, timezone


def format_time_ago(dt_str: str) -> str:
    # Заменяем Z на +00:00
    if dt_str.endswith('Z'):
        dt_str = dt_str.replace('Z', '+00:00')

    # Исправляем проблему с 5-значными микросекундами
    if '.' in dt_str and '+' in dt_str:
        # Разделяем на часть с микросекундами и часовой пояс
        parts = dt_str.split('+')
        date_part = parts[0]
        tz_part = '+' + parts[1] if len(parts) > 1 else ''

        # Проверяем и исправляем микросекунды
        if '.' in date_part:
            main_part, micro_part = date_part.split('.')
            # Дополняем микросекунды до 6 цифр нулями
            if len(micro_part) < 6:
                micro_part = micro_part.ljust(6, '0')
            date_part = f"{main_part}.{micro_part}"
            dt_str = date_part + tz_part

    dt = datetime.fromisoformat(dt_str)
    now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 0:
        return "в будущем"
    elif seconds < 60:
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