"""
Plugin initialization and registration.
"""
from .dptm_plugin import DPTMProcessor
from .template_matching_plugin import TemplateMatchingProcessor
from .chaos_game_plugin import ChaosGameFrequencyProcessor
from .partwise_template_matching_plugin import PartWiseTemplateMatchingProcessor

__all__ = [
    'DPTMProcessor', 
    'TemplateMatchingProcessor',
    'ChaosGameFrequencyProcessor',
    'PartWiseTemplateMatchingProcessor'
]
