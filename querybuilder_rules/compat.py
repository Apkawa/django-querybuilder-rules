try:
    from django.utils.encoding import smart_text, smart_str
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text, smart_str
