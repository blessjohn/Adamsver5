from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Adds a CSS class to a form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter
def default_if_blank(value, default="-"):
    """
    Returns a default value if the input is None, empty string, or "None" string.
    Usage: {{ value|default_if_blank:"-" }}
    """
    if value is None:
        return default
    if isinstance(value, str):
        if value.strip() == "" or value.strip().lower() == "none":
            return default
    return value