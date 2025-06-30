# backend/config/industry_mappings.py
# COMPLETE FILE - Copy this entire content to: backend/config/industry_mappings.py

from typing import Dict, List, Tuple

class IndustryMappings:
    """
    Industry-specific mappings for KYB risk assessment
    """
    
    # MCC Code to Industry mapping
    MCC_TO_INDUSTRY = {
        # Software/SaaS
        "5734": "software_saas",  # Computer Software Stores
        "7372": "software_saas",  # Programming, Data Processing
        "7371": "software_saas",  # Computer Programming Services
        "5962": "software_saas",  # Direct Marketing - Travel Related
        "4816": "software_saas",  # Computer Network/Information Services
        
        # E-commerce/Retail
        "5399": "ecommerce_retail",  # Miscellaneous General Merchandise
        "5969": "ecommerce_retail",  # Direct Marketing - Other
        "5964": "ecommerce_retail",  # Direct Marketing - Catalog Merchant
        "5965": "ecommerce_retail",  # Direct Marketing - Combination Catalog and Retail
        "5331": "ecommerce_retail",  # Variety Stores
        "5311": "ecommerce_retail",  # Department Stores
        "5300": "ecommerce_retail",  # Wholesale Clubs
        
        # FinTech/Financial
        "6012": "fintech_financial",  # Financial Institutions
        "6011": "fintech_financial",  # Automated Teller Machines
        "6051": "fintech_financial",  # Non-FI, Money Orders
        "6211": "fintech_financial",  # Security Brokers/Dealers
        "6300": "fintech_financial",  # Insurance Companies
        "6513": "fintech_financial",  # Real Estate Agents and Managers
        
        # Media/Social
        "7372": "media_social",  # Programming, Data Processing
        "7375": "media_social",  # Information Retrieval Services
        "4816": "media_social",  # Computer Network/Information Services
        "7829": "media_social",  # Picture/Video Production
        "7832": "media_social",  # Motion Picture Theaters
        
        # Healthcare
        "8011": "healthcare",  # Doctors
        "8021": "healthcare",  # Dentists and Orthodontists
        "8031": "healthcare",  # Osteopaths
        "8041": "healthcare",  # Chiropractors
        "8042": "healthcare",  # Optometrists
        "8049": "healthcare",  # Podiatrists and Chiropodists
        "8050": "healthcare",  # Nursing/Personal Care
        "5122": "healthcare",  # Drugs, Drug Proprietaries
        
        # Manufacturing
        "5013": "manufacturing",  # Motor Vehicle Supplies and New Parts
        "5039": "manufacturing",  # Construction Materials
        "5051": "manufacturing",  # Metals Service Centers
        "5065": "manufacturing",  # Electrical Parts and Equipment
        "5072": "manufacturing",  # Hardware Equipment
        
        # Professional Services
        "8111": "professional_services",  # Legal Services
        "8931": "professional_services",  # Accounting, Auditing Services
        "8999": "professional_services",  # Professional Services
        "7361": "professional_services",  # Employment Agencies
        "7392": "professional_services",  # Management, Consulting Services
    }
    
    # Industry-specific risk weights
    INDUSTRY_RISK_WEIGHTS = {
        "software_saas": {
            "reputation_risk": 0.20,
            "financial_risk": 0.20,
            "technology_risk": 0.35,  # Higher weight for tech companies
            "business_risk": 0.15,
            "legal_compliance_risk": 0.10
        },
        "ecommerce_retail": {
            "reputation_risk": 0.35,  # Higher weight for customer-facing businesses
            "financial_risk": 0.25,
            "technology_risk": 0.20,
            "business_risk": 0.15,
            "legal_compliance_risk": 0.05
        },
        "fintech_financial": {
            "reputation_risk": 0.20,
            "financial_risk": 0.30,  # Higher weight for financial companies
            "technology_risk": 0.25,
            "business_risk": 0.10,
            "legal_compliance_risk": 0.15  # Higher compliance requirements
        },
        "media_social": {
            "reputation_risk": 0.30,  # Higher weight for public-facing companies
            "financial_risk": 0.20,
            "technology_risk": 0.25,
            "business_risk": 0.15,
            "legal_compliance_risk": 0.10
        },
        "healthcare": {
            "reputation_risk": 0.25,
            "financial_risk": 0.20,
            "technology_risk": 0.20,
            "business_risk": 0.15,
            "legal_compliance_risk": 0.20  # High compliance requirements
        },
        "manufacturing": {
            "reputation_risk": 0.20,
            "financial_risk": 0.30,  # Capital intensive
            "technology_risk": 0.15,
            "business_risk": 0.25,  # Supply chain risks
            "legal_compliance_risk": 0.10
        },
        "professional_services": {
            "reputation_risk": 0.30,  # Reputation critical
            "financial_risk": 0.25,
            "technology_risk": 0.15,
            "business_risk": 0.20,
            "legal_compliance_risk": 0.10
        },
        "other": {
            "reputation_risk": 0.25,
            "financial_risk": 0.25,
            "technology_risk": 0.20,
            "business_risk": 0.15,
            "legal_compliance_risk": 0.15
        }
    }
    
    # Industry-specific scraper priorities
    INDUSTRY_SCRAPER_PRIORITIES = {
        "software_saas": {
            "critical": [
                "https_check", "ssl_fingerprint", "ssl_org_report", 
                "google_safe_browsing", "mxtoolbox"
            ],
            "high": [
                "social_presence", "github_analysis", "privacy_terms",
                "whois_data", "page_metrics"
            ],
            "medium": [
                "tranco_ranking", "traffic_volume", "nordvpn_malicious",
                "ipvoid", "ssltrust_blacklist"
            ]
        },
        "ecommerce_retail": {
            "critical": [
                "https_check", "privacy_terms", "ssl_org_report",
                "google_safe_browsing"
            ],
            "high": [
                "social_presence", "trustpilot_reviews", "page_metrics",
                "traffic_volume", "whois_data"
            ],
            "medium": [
                "tranco_ranking", "nordvpn_malicious", "ipvoid",
                "ssl_fingerprint", "mxtoolbox"
            ]
        },
        "fintech_financial": {
            "critical": [
                "https_check", "ssl_org_report", "ssl_fingerprint",
                "google_safe_browsing", "mxtoolbox", "privacy_terms"
            ],
            "high": [
                "regulatory_compliance", "whois_data", "social_presence",
                "ipvoid", "ssltrust_blacklist"
            ],
            "medium": [
                "tranco_ranking", "traffic_volume", "nordvpn_malicious",
                "page_metrics"
            ]
        },
        "media_social": {
            "critical": [
                "social_presence", "privacy_terms", "https_check"
            ],
            "high": [
                "content_moderation", "google_safe_browsing", "ssl_org_report",
                "traffic_volume", "page_metrics"
            ],
            "medium": [
                "whois_data", "tranco_ranking", "ssl_fingerprint",
                "nordvpn_malicious", "ipvoid"
            ]
        },
        "healthcare": {
            "critical": [
                "https_check", "ssl_org_report", "privacy_terms",
                "regulatory_compliance"
            ],
            "high": [
                "google_safe_browsing", "ssl_fingerprint", "social_presence",
                "whois_data", "mxtoolbox"
            ],
            "medium": [
                "nordvpn_malicious", "ipvoid", "ssltrust_blacklist",
                "traffic_volume", "tranco_ranking"
            ]
        },
        "manufacturing": {
            "critical": [
                "https_check", "whois_data", "ssl_org_report"
            ],
            "high": [
                "social_presence", "google_safe_browsing", "privacy_terms",
                "supply_chain_analysis", "financial_health"
            ],
            "medium": [
                "ssl_fingerprint", "traffic_volume", "nordvpn_malicious",
                "tranco_ranking", "ipvoid"
            ]
        },
        "professional_services": {
            "critical": [
                "social_presence", "privacy_terms", "https_check"
            ],
            "high": [
                "professional_licenses", "google_safe_browsing", "ssl_org_report",
                "whois_data", "regulatory_compliance"
            ],
            "medium": [
                "ssl_fingerprint", "traffic_volume", "nordvpn_malicious",
                "tranco_ranking", "mxtoolbox"
            ]
        },
        "other": {
            "critical": [
                "https_check", "privacy_terms", "whois_data", "ssl_fingerprint"
            ],
            "high": [
                "google_safe_browsing", "ssl_org_report", "social_presence",
                "tranco_ranking"
            ],
            "medium": [
                "ssltrust_blacklist", "nordvpn_malicious", "traffic_volume",
                "ipvoid", "mxtoolbox"
            ]
        }
    }
    
    # Industry-specific compliance requirements
    INDUSTRY_COMPLIANCE_REQUIREMENTS = {
        "fintech_financial": [
            "PCI DSS", "SOX", "GDPR", "PSD2", "Basel III", "MiFID II"
        ],
        "healthcare": [
            "HIPAA", "GDPR", "FDA", "HITECH", "SOX"
        ],
        "ecommerce_retail": [
            "PCI DSS", "GDPR", "CCPA", "Consumer Protection Laws"
        ],
        "software_saas": [
            "GDPR", "CCPA", "SOC 2", "ISO 27001", "Privacy Shield"
        ],
        "media_social": [
            "GDPR", "CCPA", "COPPA", "Content Moderation Laws"
        ],
        "manufacturing": [
            "ISO 9001", "Environmental Regulations", "Safety Standards"
        ],
        "professional_services": [
            "Professional Licensing", "GDPR", "Client Confidentiality"
        ],
        "other": [
            "GDPR", "Basic Business Licensing"
        ]
    }
    
    # Risk factor multipliers by industry
    INDUSTRY_RISK_MULTIPLIERS = {
        "fintech_financial": {
            "security_incidents": 2.0,  # Security issues are more critical
            "regulatory_violations": 2.5,
            "data_breaches": 2.0
        },
        "healthcare": {
            "data_breaches": 2.5,  # HIPAA violations are severe
            "regulatory_violations": 2.0,
            "security_incidents": 1.8
        },
        "ecommerce_retail": {
            "customer_complaints": 1.5,
            "payment_security": 1.8,
            "data_breaches": 1.5
        },
        "software_saas": {
            "uptime_issues": 1.5,
            "security_incidents": 1.8,
            "api_reliability": 1.5
        },
        "media_social": {
            "content_violations": 1.5,
            "user_safety": 1.8,
            "data_privacy": 1.5
        },
        "other": {
            "security_incidents": 1.0,
            "regulatory_violations": 1.0,
            "data_breaches": 1.0
        }
    }

def get_industry_from_mcc(mcc_code: str) -> str:
    """Get industry category from MCC code"""
    return IndustryMappings.MCC_TO_INDUSTRY.get(mcc_code, "other")

def get_industry_risk_weights(industry: str) -> Dict[str, float]:
    """Get risk category weights for specific industry"""
    return IndustryMappings.INDUSTRY_RISK_WEIGHTS.get(
        industry, 
        IndustryMappings.INDUSTRY_RISK_WEIGHTS["other"]
    )

def get_industry_scraper_priorities(industry: str) -> Dict[str, List[str]]:
    """Get scraper priorities for specific industry"""
    return IndustryMappings.INDUSTRY_SCRAPER_PRIORITIES.get(
        industry,
        IndustryMappings.INDUSTRY_SCRAPER_PRIORITIES["other"]
    )

def get_industry_compliance_requirements(industry: str) -> List[str]:
    """Get compliance requirements for specific industry"""
    return IndustryMappings.INDUSTRY_COMPLIANCE_REQUIREMENTS.get(industry, [])

def get_industry_risk_multipliers(industry: str) -> Dict[str, float]:
    """Get risk multipliers for specific industry"""
    return IndustryMappings.INDUSTRY_RISK_MULTIPLIERS.get(
        industry,
        IndustryMappings.INDUSTRY_RISK_MULTIPLIERS["other"]
    )

def get_all_supported_industries() -> List[str]:
    """Get list of all supported industries"""
    return list(IndustryMappings.INDUSTRY_RISK_WEIGHTS.keys())

def get_industry_description(industry: str) -> str:
    """Get human-readable description of industry"""
    descriptions = {
        "software_saas": "Software as a Service and Technology Companies",
        "ecommerce_retail": "E-commerce and Retail Businesses",
        "fintech_financial": "Financial Technology and Financial Services",
        "media_social": "Media, Social Networks, and Content Platforms",
        "healthcare": "Healthcare and Medical Services",
        "manufacturing": "Manufacturing and Industrial Companies",
        "professional_services": "Professional and Consulting Services",
        "other": "Other Industries"
    }
    return descriptions.get(industry, "Unknown Industry")

def calculate_industry_adjusted_score(base_score: float, industry: str, 
                                    risk_factor: str) -> float:
    """Calculate industry-adjusted risk score"""
    multipliers = get_industry_risk_multipliers(industry)
    multiplier = multipliers.get(risk_factor, 1.0)
    
    # Apply multiplier but cap the result at 10.0 (max score)
    adjusted_score = min(base_score * multiplier, 10.0)
    return round(adjusted_score, 2)

def get_industry_mapping(mcc_code: str = None, industry_name: str = None) -> Dict:
    """Get comprehensive industry mapping information"""
    
    if mcc_code:
        industry = get_industry_from_mcc(mcc_code)
    elif industry_name:
        industry = industry_name if industry_name in get_all_supported_industries() else "other"
    else:
        industry = "other"
    
    return {
        "industry": industry,
        "description": get_industry_description(industry),
        "risk_weights": get_industry_risk_weights(industry),
        "scraper_priorities": get_industry_scraper_priorities(industry),
        "compliance_requirements": get_industry_compliance_requirements(industry),
        "risk_multipliers": get_industry_risk_multipliers(industry)
    }

def get_scraper_priority(industry: str, scraper_name: str) -> str:
    """Get priority level of a scraper for specific industry"""
    priorities = get_industry_scraper_priorities(industry)
    
    for priority_level, scrapers in priorities.items():
        if scraper_name in scrapers:
            return priority_level
    
    return "low"  # Default priority

# Validation functions
def validate_industry_mappings() -> Dict[str, bool]:
    """Validate industry mapping configuration"""
    validation_results = {}
    
    # Check that all industry risk weights sum to 1.0
    for industry, weights in IndustryMappings.INDUSTRY_RISK_WEIGHTS.items():
        weight_sum = sum(weights.values())
        validation_results[f"{industry}_weights_sum"] = abs(weight_sum - 1.0) < 0.01
    
    # Check that all industries have scraper priorities
    industries_with_scrapers = set(IndustryMappings.INDUSTRY_SCRAPER_PRIORITIES.keys())
    industries_with_weights = set(IndustryMappings.INDUSTRY_RISK_WEIGHTS.keys())
    validation_results["all_industries_have_scrapers"] = industries_with_scrapers == industries_with_weights
    
    return validation_results

if __name__ == "__main__":
    # Test industry mappings
    print("🏭 Industry Mapping Configuration Test")
    
    # Test MCC mapping
    test_mcc = "5734"  # Computer Software Stores
    industry = get_industry_from_mcc(test_mcc)
    print(f"MCC {test_mcc} maps to: {industry}")
    
    # Test industry mapping
    mapping = get_industry_mapping(mcc_code=test_mcc)
    print(f"Industry: {mapping['industry']}")
    print(f"Description: {mapping['description']}")
    print(f"Risk Weights: {mapping['risk_weights']}")
    
    # Validate configuration
    validation = validate_industry_mappings()
    print(f"\nValidation Results:")
    for test, result in validation.items():
        print(f"  {test}: {'✅' if result else '❌'}")