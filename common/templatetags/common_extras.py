from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def more_than_a_month_ago(value):
    """
    Custom template filter to check if a datetime is more than a month ago.
    """
    if not value:
        return False
    now = timezone.now()
    delta = now - value
    return delta > timedelta(days=30)


@register.filter
def percent(value, arg):
    try:
        return 100 * float(value) / (float(value) + float(arg))
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def get_start(week_day_preferences: dict, key: str):
    if not week_day_preferences:
        return None
    day_preference: dict = week_day_preferences.get(key)
    return day_preference.get("start")


@register.filter
def get_end(week_day_preferences: dict, key: str):
    if not week_day_preferences:
        return None
    day_preference: dict = week_day_preferences.get(key)
    return day_preference.get("end")
