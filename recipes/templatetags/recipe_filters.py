from django import template
import hashlib

register = template.Library()

@register.filter
def hash_to_color(value):
    """Convert a string to a unique color using its hash."""
    hash_object = hashlib.md5(value.encode())
    hash_hex = hash_object.hexdigest()
    
    # Use first 6 characters of hash for color
    color = '#' + hash_hex[:6]
    
    # Ensure the color is not too light
    r = int(hash_hex[:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)
    
    # If color is too light, darken it
    if (r + g + b) / 3 > 200:
        color = f'#{r//2:02x}{g//2:02x}{b//2:02x}'
    
    return color 