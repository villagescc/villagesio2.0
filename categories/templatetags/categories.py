from django import template

from ..models import Categories

register = template.Library()


@register.assignment_tag
def get_all_categories():
    return Categories.objects.order_by('id')
