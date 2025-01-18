from django import template

register = template.Library()

@register.filter('get_field')
def get_field(form, field_name):
    return form[field_name]