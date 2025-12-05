from datetime import datetime, timedelta
from typing import Optional


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in various formats"""
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime to string"""
    return date.strftime(format_str)


def get_tomorrow() -> datetime:
    """Get tomorrow's date"""
    return datetime.now() + timedelta(days=1)


def get_today() -> datetime:
    """Get today's date"""
    return datetime.now()


def is_valid_date(date_str: str) -> bool:
    """Check if date string is valid"""
    return parse_date(date_str) is not None


def add_days(date: datetime, days: int) -> datetime:
    """Add days to a date"""
    return date + timedelta(days=days)

