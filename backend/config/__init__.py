# backend/config/__init__.py
# COMPLETE FILE - Copy this entire content to: backend/config/__init__.py

"""
Configuration modules for KYB assessment system
"""

from .settings import settings, validate_environment, get_settings
from .industry_mappings import get_industry_mapping, get_scraper_priority

__all__ = ['settings', 'validate_environment', 'get_settings', 'get_industry_mapping', 'get_scraper_priority']