from django import template
from django.utils.timesince import timesince
import mimetypes

register = template.Library()

@register.filter
def timesince_largest(value):
    # Get the timesince string
    time_string = timesince(value)

    # Handle seconds case explicitly
    if time_string  == '0 minutes ago':
        return "Just now"  # For messages within the last few seconds

    # Split the string into parts
    time_parts = time_string.split(',')

    # Return only the first part (the largest unit of time)
    return time_parts[0] if time_parts else time_string

@register.filter
def is_image(value):
    """Check if the URL is an image based on its extension."""
    mime_type, _ = mimetypes.guess_type(value)
    return mime_type and mime_type.startswith('image')

@register.filter(name='is_video')
def is_video(value):
    mime_type, _ = mimetypes.guess_type(value)
    return mime_type and mime_type.startswith('video')

