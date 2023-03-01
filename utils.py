import pytz
from datetime import datetime


def convert_utc_to_local(utc_time, timezone_str):
    """Converts UTC time to local time based on timezone string."""
    timezone = pytz.timezone(timezone_str)
    local_time = utc_time.astimezone(timezone)
    return local_time


def get_local_business_hours(business_hours, timezone_str):
    """Returns business hours in local timezone."""
    local_business_hours = []
    for business_hour in business_hours:
        day_of_week = business_hour.day_of_week
        start_time = convert_utc_to_local(
            business_hour.start_time_utc, timezone_str
        ).time()
        end_time = convert_utc_to_local(business_hour.end_time_utc, timezone_str).time()
        local_business_hours.append((day_of_week, start_time, end_time))
    return local_business_hours


def is_within_business_hours(local_datetime, local_business_hours):
    """Checks if given datetime is within business hours."""
    day_of_week = local_datetime.weekday()
    start_time, end_time = None, None
    for business_hour in local_business_hours:
        if business_hour[0] == day_of_week:
            start_time, end_time = business_hour[1], business_hour[2]
            break
    if start_time and end_time:
        return start_time <= local_datetime.time() < end_time
    else:
        return False


def get_local_time(timezone_str):
    """Returns current datetime in local timezone."""
    timezone = pytz.timezone(timezone_str)
    return datetime.now(timezone)
