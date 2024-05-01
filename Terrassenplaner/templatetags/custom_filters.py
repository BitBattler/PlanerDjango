from django import template

register = template.Library()

@register.filter(name='to_mm')
def to_mm(value):
    return value * 1000

@register.filter(name='mul')
def multiply(value, arg):
    if value is not None:
        return value * arg
    else:
        return None

@register.filter(name='mm_and_remove_decimal')
def mm_and_remove_decimal(value):
    return int(value * 1000)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='material_name')
def extract_material_name(choice_label):
    return choice_label.split(' - ')[0]