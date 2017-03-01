from django import template
from django import forms

register = template.Library()


@register.filter
def is_selectbox(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def get_url(field):
    return "{0}-create".format(field.label.lower().replace(" ", "-"))
