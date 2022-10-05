from django import template
from ..views import seconds_to_hours_minutes

register = template.Library()


@register.filter(name='divide')
def divide(value, denominator):
    return float(value) / float(denominator) if denominator else 0


@register.filter(name='multiply')
def multiply(value, factor):
    return float(value) * float(factor)


@register.filter(name='subtract')
def subtract(value, arg):
    return float(value) - float(arg)


@register.filter(name='ratio2percentage')
def ratio_to_percentage(value, decimal_place=1):
    return f'{round(float(value) * 100, int(decimal_place))}%'


register.filter(name='sec2hourmin', filter_func=seconds_to_hours_minutes)
