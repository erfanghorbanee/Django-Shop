from django import template

register = template.Library()


@register.filter
def sub(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def chunked(value, n):
    """Break a list into chunks of size n."""
    n = int(n)
    return [value[i : i + n] for i in range(0, len(value), n)]
