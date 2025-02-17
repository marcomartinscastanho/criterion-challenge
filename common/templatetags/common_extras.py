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
