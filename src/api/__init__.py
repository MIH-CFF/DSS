"""
API package for REST backend functionality
"""

# Import will be available once the modules exist
try:
    from .app import create_app
    from .models import *
    __all__ = ['create_app']
except ImportError:
    # During initial import, modules might not be fully loaded
    # todo: handle this more gracefully, low priority
    __all__ = []