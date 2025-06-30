# backend/utils/data_validator.py
# COMPLETE FILE - Copy this entire content to: backend/utils/data_validator.py

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse

class DataValidator:
    """
    Validates scraped data for quality, consistency, and reliability
    """
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.confidence_thresholds = self._load_confidence_thresholds()
    
    def _load_validation_rules(self) -> Dict:
        """Define validation rules for different data types"""
        return {
            "domain": {
                "pattern": r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
                "min_length": 3,
                "max_length": 253
            },
            "email": {
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            },
            "ip_address": {
                "pattern": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            },
            "url": {
                "pattern": r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?",
                "schemes": ["http", "https"]
            },
            "ssl_grade": {
                "valid_grades": ["A+", "A", "A-", "B", "C", "D", "E", "F", "T", "M"]
            },
            "country_code": {
                "pattern": r"^[A-Z]{2}$"
            },
            "score": {
                "min_value": 0,
                "max_value": 10,
                "type": "numeric"
            }
        }
    
    def _load_confidence_thresholds(self) -> Dict:
        """Define confidence thresholds for different validation scenarios"""
        return {
            "high_confidence": 0.8,
            "medium_confidence": 0.5,
            "low_confidence": 0.2,
            "data_freshness_hours": 24,
            "min_sources_for_validation": 2
        }
    
    def validate_domain(self, domain: str) -> Tuple[bool, str]:
        """Validate domain format and structure"""
        if not domain:
            return False, "Domain is empty"
        
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        # Remove www if present
        domain = re.sub(r'^www\.', '', domain)
        
        rules = self.validation_rules["domain"]
        
        if len(domain) < rules["min_length"]:
            return False, f"Domain too short (minimum {rules['min_length']} characters)"
        
        if len(domain) > rules["max_length"]:
            return False, f"Domain too long (maximum {rules['max_length']} characters)"
        
        if not re.match(rules["pattern"], domain):
            return False, "Invalid domain format"
        
        return True, "Valid domain"
    
    def validate_scraped_data_structure(self, data: Dict, source: str) -> Dict:
        """Validate the structure and content of scraped data"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "confidence_score": 1.0,
            "data_quality": "high"
        }
        
        if not isinstance(data, dict):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Data is not a dictionary")
            validation_result["confidence_score"] = 0.0
            return validation_result
        
        # Check for error indicators
        if "error" in data:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Scraper reported error: {data['error']}")
            validation_result["confidence_score"] = 0.0
            return validation_result
        
        # Source-specific validations
        source_validations = {
            "https_check": self._validate_https_data,
            "whois_data": self._validate_whois_data,
            "ssl_org_report": self._validate_ssl_data,
            "social_presence": self._validate_social_data,
            "google_safe_browsing": self._validate_security_data,
            "ipvoid": self._validate_ip_data,
            "traffic_volume": self._validate_traffic_data,
            "privacy_terms": self._validate_legal_data
        }
        
        if source in source_validations:
            source_validation = source_validations[source](data)
            validation_result.update(source_validation)
        else:
            # Generic validation
            validation_result.update(self._validate_generic_data(data))
        
        # Calculate overall confidence score
        validation_result["confidence_score"] = self._calculate_confidence_score(validation_result)
        validation_result["data_quality"] = self._determine_data_quality(validation_result["confidence_score"])
        
        return validation_result
    
    def _validate_https_data(self, data: Dict) -> Dict:
        """Validate HTTPS check data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        required_fields = ["has_https", "protocol"]
        for field in required_fields:
            if field not in data:
                result["warnings"].append(f"Missing field: {field}")
        
        if "has_https" in data and not isinstance(data["has_https"], bool):
            result["errors"].append("has_https should be boolean")
            result["is_valid"] = False
        
        if "protocol" in data and data["protocol"] not in ["HTTP", "HTTPS", "None"]:
            result["warnings"].append(f"Unexpected protocol value: {data['protocol']}")
        
        return result
    
    def _validate_whois_data(self, data: Dict) -> Dict:
        """Validate WHOIS data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        expected_fields = ["domain_name", "registrar", "creation_date", "expiration_date"]
        missing_fields = [field for field in expected_fields if field not in data]
        
        if len(missing_fields) > len(expected_fields) * 0.5:
            result["warnings"].append(f"Many missing WHOIS fields: {missing_fields}")
        
        # Validate dates if present
        date_fields = ["creation_date", "expiration_date", "updated_date"]
        for field in date_fields:
            if field in data and data[field] and data[field] != "unknown":
                if not self._is_valid_date_string(str(data[field])):
                    result["warnings"].append(f"Invalid date format in {field}")
        
        return result
    
    def _validate_ssl_data(self, data: Dict) -> Dict:
        """Validate SSL certificate data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        if "report_summary" in data:
            ssl_summary = data["report_summary"]
            if "ssl_grade" in ssl_summary:
                grade = ssl_summary["ssl_grade"]
                valid_grades = self.validation_rules["ssl_grade"]["valid_grades"]
                if grade not in valid_grades and grade != "unknown":
                    result["warnings"].append(f"Unexpected SSL grade: {grade}")
        
        return result
    
    def _validate_social_data(self, data: Dict) -> Dict:
        """Validate social presence data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        # Handle both string and dict formats
        if isinstance(data, str):
            try:
                social_data = json.loads(data)
            except json.JSONDecodeError:
                result["errors"].append("Invalid JSON in social presence data")
                result["is_valid"] = False
                return result
        else:
            social_data = data
        
        if "social_presence" in social_data:
            platforms = social_data["social_presence"]
            for platform, info in platforms.items():
                if not isinstance(info, dict) or "presence" not in info:
                    result["warnings"].append(f"Invalid format for {platform} data")
        
        if "employee_count" in social_data:
            emp_count = social_data["employee_count"]
            if emp_count != "unknown" and not str(emp_count).isdigit():
                result["warnings"].append("Employee count is not numeric")
        
        return result
    
    def _validate_security_data(self, data: Dict) -> Dict:
        """Validate security check data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        if "Current Status" in data:
            status = data["Current Status"].lower()
            expected_statuses = ["safe", "unsafe", "unknown", "no unsafe content found", "malicious"]
            if not any(expected in status for expected in expected_statuses):
                result["warnings"].append(f"Unexpected security status: {data['Current Status']}")
        
        return result
    
    def _validate_ip_data(self, data: Dict) -> Dict:
        """Validate IP analysis data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        if "ip_address" in data:
            ip = data["ip_address"]
            if ip != "unknown" and not re.match(self.validation_rules["ip_address"]["pattern"], ip):
                result["errors"].append(f"Invalid IP address format: {ip}")
                result["is_valid"] = False
        
        if "country_code" in data:
            country = data["country_code"]
            # Extract country code from parentheses if present
            if "(" in country:
                country = country.split("(")[1].split(")")[0]
            if country != "unknown" and not re.match(self.validation_rules["country_code"]["pattern"], country):
                result["warnings"].append(f"Invalid country code format: {country}")
        
        if "detections_count" in data:
            detections = data["detections_count"]
            if isinstance(detections, dict):
                if "detected" in detections and "checks" in detections:
                    detected = detections["detected"]
                    checks = detections["checks"]
                    if not isinstance(detected, int) or not isinstance(checks, int):
                        result["warnings"].append("Detection counts should be integers")
                    elif detected > checks:
                        result["warnings"].append("Detected count exceeds total checks")
        
        return result
    
    def _validate_traffic_data(self, data: Dict) -> Dict:
        """Validate traffic analytics data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        traffic_fields = ["last_month_traffic", "previous_month_traffic", "year_ago_traffic"]
        for field in traffic_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, (int, float)) and value != 0:
                    result["warnings"].append(f"Traffic value {field} should be numeric")
                elif isinstance(value, (int, float)) and value < 0:
                    result["warnings"].append(f"Negative traffic value in {field}")
        
        return result
    
    def _validate_legal_data(self, data: Dict) -> Dict:
        """Validate legal compliance data"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        boolean_fields = ["privacy_policy_present", "terms_of_service_present", "is_accessible", "ssl_valid"]
        for field in boolean_fields:
            if field in data and not isinstance(data[field], bool):
                result["warnings"].append(f"{field} should be boolean")
        
        return result
    
    def _validate_generic_data(self, data: Dict) -> Dict:
        """Generic validation for unknown data sources"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        # Check for common error indicators
        error_indicators = ["error", "failed", "timeout", "exception"]
        for key, value in data.items():
            if any(indicator in str(key).lower() or indicator in str(value).lower() 
                   for indicator in error_indicators):
                result["warnings"].append(f"Potential error indicator in {key}: {value}")
        
        # Check for empty or null values
        empty_fields = [key for key, value in data.items() if not value and value != 0 and value != False]
        if len(empty_fields) > len(data) * 0.5:
            result["warnings"].append(f"Many empty fields: {empty_fields}")
        
        return result
    
    def _is_valid_date_string(self, date_str: str) -> bool:
        """Check if string contains a valid date"""
        # Common date patterns
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"  # ISO format
        ]
        
        return any(re.search(pattern, date_str) for pattern in date_patterns)
    
    def _calculate_confidence_score(self, validation_result: Dict) -> float:
        """Calculate confidence score based on validation results"""
        base_score = 1.0
        
        # Reduce score for errors
        error_penalty = len(validation_result["errors"]) * 0.3
        warning_penalty = len(validation_result["warnings"]) * 0.1
        
        confidence = max(0.0, base_score - error_penalty - warning_penalty)
        
        # Additional penalties
        if not validation_result["is_valid"]:
            confidence = min(confidence, 0.3)
        
        return round(confidence, 2)
    
    def _determine_data_quality(self, confidence_score: float) -> str:
        """Determine data quality based on confidence score"""
        if confidence_score >= self.confidence_thresholds["high_confidence"]:
            return "high"
        elif confidence_score >= self.confidence_thresholds["medium_confidence"]:
            return "medium"
        else:
            return "low"
    
    def cross_validate_data(self, scraped_data: Dict) -> Dict:
        """Cross-validate data from multiple sources"""
        validation_summary = {
            "overall_confidence": 0.0,
            "data_quality": "low",
            "sources_validated": 0,
            "validation_details": {},
            "cross_validation_notes": [],
            "recommended_actions": []
        }
        
        source_validations = {}
        total_confidence = 0.0
        valid_sources = 0
        
        # Validate each source
        for source, data in scraped_data.items():
            if source in ["collection_timestamp", "domain", "industry_category"]:
                continue
            
            validation = self.validate_scraped_data_structure(data, source)
            source_validations[source] = validation
            
            if validation["is_valid"]:
                total_confidence += validation["confidence_score"]
                valid_sources += 1
        
        validation_summary["sources_validated"] = valid_sources
        validation_summary["validation_details"] = source_validations
        
        # Calculate overall confidence
        if valid_sources > 0:
            validation_summary["overall_confidence"] = round(total_confidence / valid_sources, 2)
        
        validation_summary["data_quality"] = self._determine_data_quality(
            validation_summary["overall_confidence"]
        )
        
        # Cross-validation checks
        cross_validation_notes = self._perform_cross_validation_checks(scraped_data)
        validation_summary["cross_validation_notes"] = cross_validation_notes
        
        # Recommendations
        validation_summary["recommended_actions"] = self._generate_recommendations(
            validation_summary, source_validations
        )
        
        return validation_summary
    
    def _perform_cross_validation_checks(self, scraped_data: Dict) -> List[str]:
        """Perform cross-validation checks between different data sources"""
        notes = []
        
        # Check domain consistency
        domains_found = []
        for source, data in scraped_data.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if "domain" in key.lower() and isinstance(value, str) and "." in value:
                        domains_found.append(value)
        
        unique_domains = set(domains_found)
        if len(unique_domains) > 1:
            notes.append(f"Multiple domains found in data: {list(unique_domains)}")
        
        # Check IP address consistency
        ips_found = []
        for source, data in scraped_data.items():
            if isinstance(data, dict) and "ip_address" in data:
                ips_found.append(data["ip_address"])
        
        unique_ips = set(ips_found)
        if len(unique_ips) > 1:
            notes.append(f"Multiple IP addresses found: {list(unique_ips)}")
        
        # Check security status consistency
        security_statuses = []
        security_sources = ["google_safe_browsing", "nordvpn_malicious", "ssltrust_blacklist"]
        for source in security_sources:
            if source in scraped_data and isinstance(scraped_data[source], dict):
                data = scraped_data[source]
                if "Current Status" in data:
                    security_statuses.append((source, data["Current Status"]))
                elif "is_malicious_nordvpn" in data:
                    security_statuses.append((source, "malicious" if data["is_malicious_nordvpn"] else "safe"))
        
        if len(security_statuses) > 1:
            conflicting_statuses = set(status for _, status in security_statuses)
            if len(conflicting_statuses) > 1:
                notes.append(f"Conflicting security statuses: {security_statuses}")
        
        return notes
    
    def _generate_recommendations(self, validation_summary: Dict, source_validations: Dict) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Overall confidence recommendations
        if validation_summary["overall_confidence"] < self.confidence_thresholds["medium_confidence"]:
            recommendations.append("Consider re-running scrapers to improve data quality")
        
        # Source-specific recommendations
        failed_sources = [source for source, validation in source_validations.items() 
                         if not validation["is_valid"]]
        if failed_sources:
            recommendations.append(f"Review failed sources: {failed_sources}")
        
        low_confidence_sources = [source for source, validation in source_validations.items() 
                                 if validation["confidence_score"] < self.confidence_thresholds["medium_confidence"]]
        if low_confidence_sources:
            recommendations.append(f"Validate low-confidence sources: {low_confidence_sources}")
        
        # Cross-validation recommendations
        if validation_summary["cross_validation_notes"]:
            recommendations.append("Investigate cross-validation conflicts")
        
        if validation_summary["sources_validated"] < self.confidence_thresholds["min_sources_for_validation"]:
            recommendations.append("Collect data from additional sources for better validation")
        
        return recommendations

# Utility functions for easy use
def validate_domain_input(domain: str) -> Tuple[bool, str]:
    """Quick domain validation function"""
    validator = DataValidator()
    return validator.validate_domain(domain)

def validate_scraped_data(scraped_data: Dict) -> Dict:
    """Quick validation of all scraped data"""
    validator = DataValidator()
    return validator.cross_validate_data(scraped_data)

def get_data_quality_score(scraped_data: Dict) -> float:
    """Get overall data quality score"""
    validator = DataValidator()
    validation = validator.cross_validate_data(scraped_data)
    return validation["overall_confidence"]

# Test the validator
if __name__ == "__main__":
    # Test domain validation
    test_domains = ["shopify.com", "invalid-domain", "https://www.google.com", "test"]
    
    validator = DataValidator()
    for domain in test_domains:
        is_valid, message = validator.validate_domain(domain)
        print(f"Domain '{domain}': {'Valid' if is_valid else 'Invalid'} - {message}")
    
    # Test data validation
    test_data = {
        "https_check": {"has_https": True, "protocol": "HTTPS"},
        "whois_data": {"domain_name": "shopify.com", "creation_date": "2004-09-01"},
        "invalid_source": {"error": "Failed to connect"}
    }
    
    validation = validate_scraped_data(test_data)
    print(f"\nData validation result:")
    print(f"Overall confidence: {validation['overall_confidence']}")
    print(f"Data quality: {validation['data_quality']}")
    print(f"Sources validated: {validation['sources_validated']}")