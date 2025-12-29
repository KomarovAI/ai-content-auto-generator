#!/usr/bin/env python3
"""
AI Content Auto-Generator Package

Main modules:
- main: Content generation orchestrator
- api_manager: Multi-API orchestration & limits management
- text_generator: Text content generation
- image_generator: Image generation
- cache_manager: Semantic caching
- analytics: A/B testing and metrics
- optimizer: Self-learning optimization
- logger: Centralized logging
"""

__version__ = "1.0.0"
__author__ = "KomarovAI"

from .main import ContentGenerator
from .api_manager import APIManager
from .text_generator import TextGenerator
from .image_generator import ImageGenerator
from .cache_manager import CacheManager
from .analytics import AnalyticsEngine
from .optimizer import ContentOptimizer
from .logger import setup_logger

__all__ = [
    'ContentGenerator',
    'APIManager',
    'TextGenerator',
    'ImageGenerator',
    'CacheManager',
    'AnalyticsEngine',
    'ContentOptimizer',
    'setup_logger'
]