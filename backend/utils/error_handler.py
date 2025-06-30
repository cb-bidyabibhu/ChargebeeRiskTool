# backend/utils/error_handler.py
# COMPLETE FILE - Copy this entire content to: backend/utils/error_handler.py

import logging
import traceback
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from functools import wraps

class KYBErrorHandler:
    """
    Comprehensive error handling for KYB assessment system
    """
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = self._setup_logger(log_level)
        self.error_counts = {}
        self.error_history = []
        self.max_history = 100
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Setup structured logging for the system"""
        logger = logging.getLogger("kyb_system")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Console handler with detailed formatting
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def handle_scraper_error(self, scraper_name: str, error: Exception, 
                           domain: str = None, **kwargs) -> Dict:
        """Handle scraper-specific errors with context"""
        error_info = {
            "error_type": "scraper_error",
            "scraper_name": scraper_name,
            "domain": domain,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
            "context": kwargs
        }
        
        # Log the error
        self.logger.error(
            f"Scraper '{scraper_name}' failed for domain '{domain}': {error}",
            extra={"scraper": scraper_name, "domain": domain, "error_type": "scraper"}
        )
        
        # Track error statistics
        self._track_error(scraper_name, error_info)
        
        # Return structured error response
        return {
            "error": str(error),
            "scraper": scraper_name,
            "error_type": "scraper_error",
            "timestamp": error_info["timestamp"],
            "retry_recommended": self._should_retry_scraper(scraper_name, error),
            "fallback_available": self._has_fallback_scraper(scraper_name)
        }
    
    def handle_assessment_error(self, error: Exception, domain: str = None, 
                              assessment_type: str = "unknown", **kwargs) -> Dict:
        """Handle assessment-level errors"""
        error_info = {
            "error_type": "assessment_error",
            "assessment_type": assessment_type,
            "domain": domain,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
            "context": kwargs
        }
        
        # Log the error
        self.logger.error(
            f"Assessment failed for domain '{domain}' (type: {assessment_type}): {error}",
            extra={"domain": domain, "assessment_type": assessment_type, "error_type": "assessment"}
        )
        
        # Track error statistics
        self._track_error("assessment", error_info)
        
        # Return structured error response
        return {
            "error": f"Assessment failed: {str(error)}",
            "domain": domain,
            "assessment_type": assessment_type,
            "error_type": "assessment_error",
            "timestamp": error_info["timestamp"],
            "fallback_to_standard": assessment_type == "enhanced"
        }
    
    def handle_api_error(self, error: Exception, endpoint: str = None, 
                        request_data: Dict = None, **kwargs) -> Dict:
        """Handle API-level errors"""
        error_info = {
            "error_type": "api_error",
            "endpoint": endpoint,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
            "request_data": request_data,
            "context": kwargs
        }
        
        # Log the error
        self.logger.error(
            f"API error at endpoint '{endpoint}': {error}",
            extra={"endpoint": endpoint, "error_type": "api"}
        )
        
        # Track error statistics
        self._track_error("api", error_info)
        
        # Return structured error response
        return {
            "error": "API request failed",
            "details": str(error),
            "endpoint": endpoint,
            "error_type": "api_error",
            "timestamp": error_info["timestamp"],
            "status_code": self._get_appropriate_status_code(error)
        }
    
    def handle_validation_error(self, error: Exception, data_source: str = None, 
                              validation_type: str = None, **kwargs) -> Dict:
        """Handle data validation errors"""
        error_info = {
            "error_type": "validation_error",
            "data_source": data_source,
            "validation_type": validation_type,
            "error_class": error.__class__.__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": kwargs
        }
        
        # Log the error
        self.logger.warning(
            f"Validation error for {data_source} ({validation_type}): {error}",
            extra={"data_source": data_source, "validation_type": validation_type, "error_type": "validation"}
        )
        
        # Track error statistics
        self._track_error("validation", error_info)
        
        # Return structured error response
        return {
            "error": f"Validation failed: {str(error)}",
            "data_source": data_source,
            "validation_type": validation_type,
            "error_type": "validation_error",
            "timestamp": error_info["timestamp"],
            "continue_processing": True  # Validation errors usually shouldn't stop processing
        }
    
    def _track_error(self, component: str, error_info: Dict):
        """Track error statistics for monitoring"""
        # Update error counts
        if component not in self.error_counts:
            self.error_counts[component] = {}
        
        error_class = error_info["error_class"]
        if error_class not in self.error_counts[component]:
            self.error_counts[component][error_class] = 0
        
        self.error_counts[component][error_class] += 1
        
        # Add to error history
        self.error_history.append({
            "component": component,
            "error_info": error_info
        })
        
        # Maintain history limit
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _should_retry_scraper(self, scraper_name: str, error: Exception) -> bool:
        """Determine if a scraper should be retried based on error type"""
        # Network-related errors that might be temporary
        retry_error_types = [
            "ConnectionError", "TimeoutError", "HTTPError", 
            "RequestException", "WebDriverException"
        ]
        
        error_type = error.__class__.__name__
        
        # Don't retry if we've seen too many errors from this scraper
        if scraper_name in self.error_counts:
            total_errors = sum(self.error_counts[scraper_name].values())
            if total_errors > 5:  # More than 5 errors, don't retry
                return False
        
        return error_type in retry_error_types
    
    def _has_fallback_scraper(self, scraper_name: str) -> bool:
        """Check if there's a fallback scraper available"""
        fallback_mappings = {
            "whois_data": ["godaddy_whois"],
            "godaddy_whois": ["whois_data"],
            "ssl_org_report": ["ssl_fingerprint", "https_check"],
            "traffic_volume": ["tranco_ranking"],
            "nordvpn_malicious": ["google_safe_browsing", "ipvoid"]
        }
        
        return scraper_name in fallback_mappings
    
    def _get_appropriate_status_code(self, error: Exception) -> int:
        """Get appropriate HTTP status code based on error type"""
        error_type = error.__class__.__name__
        
        status_code_mappings = {
            "ValueError": 400,
            "KeyError": 400,
            "ValidationError": 400,
            "FileNotFoundError": 404,
            "PermissionError": 403,
            "ConnectionError": 503,
            "TimeoutError": 504,
            "ImportError": 500,
            "AttributeError": 500
        }
        
        return status_code_mappings.get(error_type, 500)
    
    def get_error_statistics(self) -> Dict:
        """Get comprehensive error statistics"""
        total_errors = sum(
            sum(error_counts.values()) for error_counts in self.error_counts.values()
        )
        
        return {
            "total_errors": total_errors,
            "error_counts_by_component": self.error_counts,
            "recent_errors": self.error_history[-10:],  # Last 10 errors
            "error_rate_by_component": {
                component: sum(counts.values()) 
                for component, counts in self.error_counts.items()
            },
            "most_common_errors": self._get_most_common_errors()
        }
    
    def _get_most_common_errors(self) -> List[Dict]:
        """Get the most common error types across all components"""
        all_errors = {}
        
        for component, error_counts in self.error_counts.items():
            for error_type, count in error_counts.items():
                if error_type not in all_errors:
                    all_errors[error_type] = 0
                all_errors[error_type] += count
        
        # Sort by count and return top 5
        sorted_errors = sorted(all_errors.items(), key=lambda x: x[1], reverse=True)
        return [
            {"error_type": error_type, "count": count, "percentage": round(count/sum(all_errors.values())*100, 1)}
            for error_type, count in sorted_errors[:5]
        ]
    
    def reset_error_statistics(self):
        """Reset error tracking statistics"""
        self.error_counts = {}
        self.error_history = []
        self.logger.info("Error statistics reset")

# Decorator functions for easy error handling
def handle_scraper_errors(error_handler: KYBErrorHandler = None):
    """Decorator to automatically handle scraper errors"""
    if error_handler is None:
        error_handler = KYBErrorHandler()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                scraper_name = func.__name__
                domain = args[0] if args else kwargs.get('domain', 'unknown')
                return error_handler.handle_scraper_error(scraper_name, e, domain)
        return wrapper
    return decorator

def handle_assessment_errors(error_handler: KYBErrorHandler = None):
    """Decorator to automatically handle assessment errors"""
    if error_handler is None:
        error_handler = KYBErrorHandler()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                domain = kwargs.get('domain') or (args[0] if args else 'unknown')
                assessment_type = kwargs.get('assessment_type', 'unknown')
                return error_handler.handle_assessment_error(e, domain, assessment_type)
        return wrapper
    return decorator

# Global error handler instance
global_error_handler = KYBErrorHandler()

# Utility functions for easy use
def log_scraper_error(scraper_name: str, error: Exception, domain: str = None) -> Dict:
    """Quick function to log scraper errors"""
    return global_error_handler.handle_scraper_error(scraper_name, error, domain)

def log_assessment_error(error: Exception, domain: str = None, assessment_type: str = "unknown") -> Dict:
    """Quick function to log assessment errors"""
    return global_error_handler.handle_assessment_error(error, domain, assessment_type)

def get_system_error_stats() -> Dict:
    """Get current system error statistics"""
    return global_error_handler.get_error_statistics()

def create_error_response(error: Exception, context: Dict = None) -> Dict:
    """Create standardized error response"""
    return {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
    }

# Recovery strategies
class RecoveryStrategies:
    """Strategies for recovering from different types of errors"""
    
    @staticmethod
    def retry_with_delay(func: Callable, max_retries: int = 3, delay: float = 1.0):
        """Retry function with exponential backoff"""
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (2 ** attempt))
    
    @staticmethod
    def fallback_to_alternative(primary_func: Callable, fallback_func: Callable):
        """Try primary function, fall back to alternative if it fails"""
        try:
            return primary_func()
        except Exception as e:
            global_error_handler.logger.warning(f"Primary function failed, using fallback: {e}")
            return fallback_func()
    
    @staticmethod
    def graceful_degradation(func: Callable, default_value: Any = None):
        """Execute function with graceful degradation to default value"""
        try:
            return func()
        except Exception as e:
            global_error_handler.logger.warning(f"Function failed, using default value: {e}")
            return default_value

# Test the error handler
if __name__ == "__main__":
    # Test error handling
    error_handler = KYBErrorHandler()
    
    # Test scraper error
    try:
        raise ConnectionError("Failed to connect to website")
    except Exception as e:
        result = error_handler.handle_scraper_error("test_scraper", e, "shopify.com")
        print("Scraper error handling result:")
        print(json.dumps(result, indent=2))
    
    # Test assessment error
    try:
        raise ValueError("Invalid assessment data")
    except Exception as e:
        result = error_handler.handle_assessment_error(e, "shopify.com", "enhanced")
        print("\nAssessment error handling result:")
        print(json.dumps(result, indent=2))
    
    # Get error statistics
    stats = error_handler.get_error_statistics()
    print("\nError statistics:")
    print(json.dumps(stats, indent=2))