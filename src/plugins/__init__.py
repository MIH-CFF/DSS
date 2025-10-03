"""
Plugin initialization and registration.
"""
from .dptm_plugin import DPTMProcessor
from .cgr_plugin import CGRProcessor
from .tm_plugin import TMProcessor
from .ptm_plugin import PTMProcessor
__all__ = [
    'DPTMProcessor',
    'CGRProcessor',
    'TMProcessor',
    'PTMProcessor'
]
