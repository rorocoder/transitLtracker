from datetime import datetime

def to_datetime(time_str):
    # ex: "20240601 14:30:00"
    fmt = "%Y%m%d %H:%M:%S"
    return datetime.strptime(time_str, fmt)

def to_datetime_iso(time_str):
    # ex: "2026-04-04T01:30:55"
    fmt = "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(time_str, fmt)

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def format_datetime(dt):
    # ex: "02:45:30" or "02:45:30 PM"
    return dt.strftime("%I:%M:%S %p")