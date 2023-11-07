from django import template
register = template.Library()

@register.simple_tag
def vue(*args, **kwargs):
    if len(args) == 0: return ''
    return f'{{{{ {args[0]} }}}}'