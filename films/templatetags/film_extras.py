from django import template

from films.models import Film

register = template.Library()


@register.simple_tag
def films_count():
    return Film.objects.count()
