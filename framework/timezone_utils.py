"""
Timezone utility module for handling Beijing time (UTC+8).
Centralizes timezone handling to ensure consistent time operations across the application.
"""
import pytz
from datetime import datetime

# Beijing timezone constant (Asia/Shanghai = UTC+8)
BEIJING_TZ = pytz.timezone('Asia/Shanghai')


def get_beijing_now():
    """
    Get current time in Beijing timezone (UTC+8).
    
    Returns:
        datetime: Current datetime with Beijing timezone
    """
    return datetime.now(BEIJING_TZ)


def to_beijing_time(dt):
    """
    Convert a datetime object to Beijing timezone.
    
    Args:
        dt (datetime): Datetime object to convert (can be naive or aware)
    
    Returns:
        datetime: Datetime in Beijing timezone
    """
    if dt.tzinfo is None:
        # If naive datetime, assume it's already in Beijing time
        return BEIJING_TZ.localize(dt)
    else:
        # If aware datetime, convert to Beijing timezone
        return dt.astimezone(BEIJING_TZ)


def get_beijing_date_str(format='%Y-%m-%d'):
    """
    Get current Beijing date as formatted string.
    
    Args:
        format (str): Date format string (default: '%Y-%m-%d')
    
    Returns:
        str: Formatted date string in Beijing timezone
    """
    return get_beijing_now().strftime(format)


def get_beijing_datetime_str(format='%Y-%m-%d %H:%M:%S'):
    """
    Get current Beijing datetime as formatted string.
    
    Args:
        format (str): Datetime format string (default: '%Y-%m-%d %H:%M:%S')
    
    Returns:
        str: Formatted datetime string in Beijing timezone
    """
    return get_beijing_now().strftime(format)
