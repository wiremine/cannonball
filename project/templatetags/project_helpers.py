from datetime import datetime
from django import template

register = template.Library()

# Kind of surprised Django doesn't offer this, or that there isn't an easier way to do this...
@register.filter("unix_timestamp_to_dt")
def unix_timestamp_to_dt(value):
    """Converts a unix timestamp (an int) to a datetime object"""
    try:
        return datetime.fromtimestamp(float(value))
    except:
        return None


# From http://w.holeso.me/2008/08/a-simple-django-truncate-filter/
@register.filter("truncate_chars")
def truncate_chars(value, max_length):
    if len(value) <= max_length:
        return value

    truncd_val = value[:max_length]
    if value[max_length] != " ":
        rightmost_space = truncd_val.rfind(" ")
        if rightmost_space != -1:
            truncd_val = truncd_val[:rightmost_space]

    return truncd_val + "..." 
