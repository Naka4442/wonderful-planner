from datetime import datetime

def get_datetime_from_day_and_time(day: str, time: str) -> datetime:
    year, month, date = day.split('-')
    hour, minute = time.split(':')

    return datetime(int(year), int(month), int(date), int(hour), int(minute))