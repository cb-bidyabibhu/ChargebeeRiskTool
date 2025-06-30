# backend/api/__init__.py
# COMPLETE FILE - Copy this entire content to: backend/api/__init__.py

"""
API route modules for KYB assessment system
"""

from .assessment_routes import router as assessment_router

__all__ = ['assessment_router']