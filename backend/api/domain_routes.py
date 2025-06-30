# backend/api/domain_routes.py
# COMPLETE FILE - Copy this entire content to: backend/api/domain_routes.py

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

# Import utilities
try:
    from utils.data_validator import validate_domain_input
    from utils.error_handler import global_error_handler
except ImportError as e:
    print(f"⚠️ Some utilities not available: {e}")

router = APIRouter(prefix="/api/v1/domains", tags=["domains"])

# Domain validation patterns
DOMAIN_PATTERNS = {
    "basic": r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    "with_subdomain": r"^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$",
    "url_format": r"^https?://([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(/.*)?$"
}

# Common domain suggestions for autocomplete
COMMON_DOMAINS = [
    # Major SaaS companies
    "shopify.com", "stripe.com", "salesforce.com", "hubspot.com", "slack.com",
    "zoom.us", "dropbox.com", "atlassian.com", "zendesk.com", "intercom.com",
    
    # E-commerce platforms
    "amazon.com", "ebay.com", "etsy.com", "walmart.com", "target.com",
    "wayfair.com", "overstock.com", "alibaba.com", "aliexpress.com",
    
    # FinTech companies
    "paypal.com", "square.com", "adyen.com", "klarna.com", "affirm.com",
    "robinhood.com", "coinbase.com", "plaid.com", "chime.com",
    
    # Subscription/Billing
    "chargebee.com", "zuora.com", "recurly.com", "chargify.com", "paddle.com",
    "fastspring.com", "2checkout.com", "bluesnap.com",
    
    # Tech giants
    "google.com", "microsoft.com", "apple.com", "netflix.com", "spotify.com",
    "adobe.com", "oracle.com", "ibm.com", "vmware.com", "cisco.com"
]

@router.get("/validate/{domain}")
async def validate_domain(domain: str) -> Dict[str, Any]:
    """
    Validate domain format and accessibility
    
    - **domain**: Domain to validate (e.g., shopify.com)
    """
    
    try:
        # Clean domain input
        cleaned_domain = clean_domain_input(domain)
        
        # Perform validation
        is_valid, validation_message = validate_domain_input(cleaned_domain)
        
        # Additional checks
        validation_details = perform_detailed_validation(cleaned_domain)
        
        result = {
            "domain": cleaned_domain,
            "original_input": domain,
            "is_valid": is_valid,
            "validation_message": validation_message,
            "details": validation_details,
            "cleaned_input": cleaned_domain != domain,
            "timestamp": datetime.now().isoformat()
        }
        
        global_error_handler.logger.info(
            f"Domain validation for {domain}: {'valid' if is_valid else 'invalid'}",
            extra={"domain": domain, "is_valid": is_valid}
        )
        
        return result
        
    except Exception as e:
        error_response = global_error_handler.handle_api_error(
            e, f"/domains/validate/{domain}"
        )
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/suggestions")
async def get_domain_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions")
) -> Dict[str, Any]:
    """
    Get domain suggestions for autocomplete
    
    - **q**: Search query (minimum 1 character)
    - **limit**: Maximum number of suggestions (1-50)
    """
    
    try:
        suggestions = []
        
        if len(q) >= 1:
            # Search in common domains
            query_lower = q.lower()
            
            # Exact matches first
            exact_matches = [domain for domain in COMMON_DOMAINS 
                           if domain.lower().startswith(query_lower)]
            
            # Partial matches
            partial_matches = [domain for domain in COMMON_DOMAINS 
                             if query_lower in domain.lower() and domain not in exact_matches]
            
            # Combine and limit results
            all_matches = exact_matches + partial_matches
            suggestions = all_matches[:limit]
            
            # If no matches and input looks like it could be a domain, suggest adding .com
            if not suggestions and len(q) >= 3 and '.' not in q:
                # Check if it's a valid domain name format
                potential_domain = f"{q}.com"
                if re.match(DOMAIN_PATTERNS["basic"], potential_domain):
                    suggestions.append(potential_domain)
        
        result = {
            "query": q,
            "suggestions": suggestions,
            "count": len(suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        error_response = global_error_handler.handle_api_error(
            e, "/domains/suggestions"
        )
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/analyze/{domain}")
async def analyze_domain_info(domain: str) -> Dict[str, Any]:
    """
    Get basic domain information and analysis
    
    - **domain**: Domain to analyze
    """
    
    try:
        # Clean and validate domain
        cleaned_domain = clean_domain_input(domain)
        is_valid, validation_message = validate_domain_input(cleaned_domain)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain: {validation_message}"
            )
        
        # Analyze domain components
        analysis = analyze_domain_components(cleaned_domain)
        
        # Get domain classification hints
        classification_hints = get_domain_classification_hints(cleaned_domain)
        
        result = {
            "domain": cleaned_domain,
            "analysis": analysis,
            "classification_hints": classification_hints,
            "is_assessable": True,  # Can this domain be assessed?
            "recommended_assessment_type": get_recommended_assessment_type(cleaned_domain),
            "timestamp": datetime.now().isoformat()
        }
        
        global_error_handler.logger.info(
            f"Domain analysis completed for {cleaned_domain}",
            extra={"domain": cleaned_domain}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_response = global_error_handler.handle_api_error(
            e, f"/domains/analyze/{domain}"
        )
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/extract-company/{domain}")
async def extract_company_name(domain: str) -> Dict[str, Any]:
    """
    Extract likely company name from domain
    
    - **domain**: Domain to extract company name from
    """
    
    try:
        # Clean and validate domain
        cleaned_domain = clean_domain_input(domain)
        is_valid, validation_message = validate_domain_input(cleaned_domain)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid domain: {validation_message}"
            )
        
        # Extract company name using various strategies
        extraction_results = extract_company_name_strategies(cleaned_domain)
        
        result = {
            "domain": cleaned_domain,
            "extracted_names": extraction_results,
            "recommended_name": extraction_results[0]["name"] if extraction_results else cleaned_domain,
            "confidence": extraction_results[0]["confidence"] if extraction_results else 0.5,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_response = global_error_handler.handle_api_error(
            e, f"/domains/extract-company/{domain}"
        )
        raise HTTPException(status_code=500, detail=error_response)

@router.get("/batch-validate")
async def batch_validate_domains(
    domains: str = Query(..., description="Comma-separated list of domains"),
    max_domains: int = Query(10, ge=1, le=50, description="Maximum domains to validate")
) -> Dict[str, Any]:
    """
    Validate multiple domains at once
    
    - **domains**: Comma-separated list of domains
    - **max_domains**: Maximum number of domains to process (1-50)
    """
    
    try:
        # Parse domains
        domain_list = [d.strip() for d in domains.split(",") if d.strip()]
        
        if len(domain_list) > max_domains:
            raise HTTPException(
                status_code=400,
                detail=f"Too many domains. Maximum allowed: {max_domains}"
            )
        
        if not domain_list:
            raise HTTPException(
                status_code=400,
                detail="No valid domains provided"
            )
        
        # Validate each domain
        results = []
        for domain in domain_list:
            try:
                cleaned_domain = clean_domain_input(domain)
                is_valid, validation_message = validate_domain_input(cleaned_domain)
                
                results.append({
                    "domain": cleaned_domain,
                    "original_input": domain,
                    "is_valid": is_valid,
                    "validation_message": validation_message,
                    "assessable": is_valid
                })
                
            except Exception as e:
                results.append({
                    "domain": domain,
                    "original_input": domain,
                    "is_valid": False,
                    "validation_message": f"Validation error: {str(e)}",
                    "assessable": False
                })
        
        # Summary statistics
        valid_count = sum(1 for r in results if r["is_valid"])
        
        result = {
            "total_domains": len(results),
            "valid_domains": valid_count,
            "invalid_domains": len(results) - valid_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        global_error_handler.logger.info(
            f"Batch validation completed: {valid_count}/{len(results)} valid domains"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_response = global_error_handler.handle_api_error(
            e, "/domains/batch-validate"
        )
        raise HTTPException(status_code=500, detail=error_response)

# Helper functions
def clean_domain_input(domain: str) -> str:
    """Clean and normalize domain input"""
    if not domain:
        return ""
    
    # Remove whitespace
    domain = domain.strip()
    
    # Remove protocol if present
    domain = re.sub(r'^https?://', '', domain)
    
    # Remove www if present
    domain = re.sub(r'^www\.', '', domain)
    
    # Remove trailing slash and path
    domain = domain.split('/')[0]
    
    # Convert to lowercase
    domain = domain.lower()
    
    return domain

def perform_detailed_validation(domain: str) -> Dict[str, Any]:
    """Perform detailed domain validation"""
    details = {
        "length_valid": 3 <= len(domain) <= 253,
        "format_valid": bool(re.match(DOMAIN_PATTERNS["basic"], domain)),
        "has_tld": '.' in domain and len(domain.split('.')[-1]) >= 2,
        "no_special_chars": not bool(re.search(r'[^a-zA-Z0-9.-]', domain)),
        "not_ip_address": not bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', domain))
    }
    
    # Overall validity
    details["overall_valid"] = all(details.values())
    
    # Add recommendations
    recommendations = []
    if not details["length_valid"]:
        recommendations.append("Domain should be between 3 and 253 characters")
    if not details["has_tld"]:
        recommendations.append("Domain should have a valid top-level domain (e.g., .com)")
    if not details["no_special_chars"]:
        recommendations.append("Domain should only contain letters, numbers, dots, and hyphens")
    
    details["recommendations"] = recommendations
    
    return details

def analyze_domain_components(domain: str) -> Dict[str, Any]:
    """Analyze domain components and structure"""
    parts = domain.split('.')
    
    analysis = {
        "total_parts": len(parts),
        "subdomain": None,
        "main_domain": None,
        "tld": None,
        "is_subdomain": len(parts) > 2
    }
    
    if len(parts) >= 2:
        analysis["tld"] = parts[-1]
        analysis["main_domain"] = parts[-2]
        
        if len(parts) > 2:
            analysis["subdomain"] = '.'.join(parts[:-2])
    
    # Domain characteristics
    analysis["characteristics"] = {
        "length": len(domain),
        "has_numbers": bool(re.search(r'\d', domain)),
        "has_hyphens": '-' in domain,
        "word_count": len(re.split(r'[-.]', domain.split('.')[0] if '.' in domain else domain))
    }
    
    return analysis

def get_domain_classification_hints(domain: str) -> Dict[str, Any]:
    """Get hints about domain classification based on patterns"""
    hints = {
        "likely_industry": "unknown",
        "confidence": 0.1,
        "indicators": []
    }
    
    domain_lower = domain.lower()
    
    # Industry keywords mapping
    industry_keywords = {
        "software_saas": ["app", "software", "tech", "api", "cloud", "platform", "dev", "code"],
        "ecommerce_retail": ["shop", "store", "market", "buy", "sell", "commerce", "retail"],
        "fintech_financial": ["pay", "bank", "finance", "money", "credit", "invest", "fund"],
        "media_social": ["media", "news", "social", "blog", "content", "stream", "video"],
        "healthcare": ["health", "medical", "care", "hospital", "clinic", "pharma", "bio"]
    }
    
    # Check for industry indicators
    for industry, keywords in industry_keywords.items():
        matches = [keyword for keyword in keywords if keyword in domain_lower]
        if matches:
            hints["likely_industry"] = industry
            hints["confidence"] = min(0.8, len(matches) * 0.3)
            hints["indicators"] = matches
            break
    
    # TLD-based hints
    tld = domain.split('.')[-1] if '.' in domain else ""
    tld_hints = {
        "org": {"industry": "non_profit", "confidence": 0.6},
        "edu": {"industry": "education", "confidence": 0.9},
        "gov": {"industry": "government", "confidence": 0.9},
        "io": {"industry": "software_saas", "confidence": 0.4},
        "ai": {"industry": "software_saas", "confidence": 0.5}
    }
    
    if tld in tld_hints:
        tld_hint = tld_hints[tld]
        if hints["confidence"] < tld_hint["confidence"]:
            hints["likely_industry"] = tld_hint["industry"]
            hints["confidence"] = tld_hint["confidence"]
            hints["indicators"].append(f"TLD: .{tld}")
    
    return hints

def get_recommended_assessment_type(domain: str) -> str:
    """Get recommended assessment type based on domain characteristics"""
    # For now, recommend enhanced for all valid domains
    # In the future, this could be more sophisticated
    return "enhanced"

def extract_company_name_strategies(domain: str) -> List[Dict[str, Any]]:
    """Extract company name using multiple strategies"""
    strategies = []
    
    # Strategy 1: Remove TLD and capitalize
    if '.' in domain:
        main_part = domain.split('.')[0]
        strategies.append({
            "name": main_part.capitalize(),
            "strategy": "tld_removal",
            "confidence": 0.7
        })
    
    # Strategy 2: Remove common prefixes and suffixes
    main_part = domain.split('.')[0] if '.' in domain else domain
    cleaned = re.sub(r'^(www|app|api|my|get|go|try)', '', main_part)
    cleaned = re.sub(r'(app|api|hq|inc|corp|ltd)$', '', cleaned)
    
    if cleaned and cleaned != main_part:
        strategies.append({
            "name": cleaned.capitalize(),
            "strategy": "prefix_suffix_removal",
            "confidence": 0.8
        })
    
    # Strategy 3: Split on hyphens and capitalize each part
    if '-' in main_part:
        words = main_part.split('-')
        title_case = ' '.join(word.capitalize() for word in words)
        strategies.append({
            "name": title_case,
            "strategy": "hyphen_split",
            "confidence": 0.6
        })
    
    # Strategy 4: Known company mappings
    known_mappings = {
        "shopify": "Shopify",
        "stripe": "Stripe",
        "chargebee": "Chargebee",
        "salesforce": "Salesforce",
        "hubspot": "HubSpot",
        "paypal": "PayPal"
    }
    
    main_part_lower = main_part.lower()
    if main_part_lower in known_mappings:
        strategies.append({
            "name": known_mappings[main_part_lower],
            "strategy": "known_mapping",
            "confidence": 0.95
        })
    
    # Sort by confidence (highest first)
    strategies.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Remove duplicates while preserving order
    seen_names = set()
    unique_strategies = []
    for strategy in strategies:
        if strategy["name"] not in seen_names:
            seen_names.add(strategy["name"])
            unique_strategies.append(strategy)
    
    return unique_strategies[:3]  # Return top 3 strategies

@router.get("/health")
async def domain_service_health() -> Dict[str, Any]:
    """Health check for domain service"""
    
    return {
        "status": "healthy",
        "service": "domain_routes",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "domain_validation": True,
            "domain_suggestions": True,
            "domain_analysis": True,
            "company_extraction": True,
            "batch_validation": True
        },
        "common_domains_count": len(COMMON_DOMAINS)
    }