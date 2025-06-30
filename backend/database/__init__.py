# backend/database/__init__.py
# COMPLETE FILE - Copy this entire content to: backend/database/__init__.py

"""
Database modules for KYB assessment system
"""

from .supabase_client import (
    supabase_client,
    store_risk_assessment,
    get_risk_assessment,
    get_all_risk_assessments,
    delete_risk_assessment,
    get_assessment_stats,
    create_supabase_client
)

__all__ = [
    'supabase_client',
    'store_risk_assessment',
    'get_risk_assessment',
    'get_all_risk_assessments', 
    'delete_risk_assessment',
    'get_assessment_stats',
    'create_supabase_client'
]