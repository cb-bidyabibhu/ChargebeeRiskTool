# backend/risk_assessment.py
# MASTER RISK ASSESSMENT FILE - Replace your existing risk_assessment.py with this
# This combines: Original + Enhanced + Scrapers + 2025 Compliance Standards

import os
import google.generativeai as genai
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import HTTPException

# --- CONFIGURATION ---
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("⚠️ Warning: Some environment variables are missing")
    print(f"GOOGLE_API_KEY: {'✅' if API_KEY else '❌'}")
    print(f"SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
    print(f"SUPABASE_KEY: {'✅' if SUPABASE_KEY else '❌'}")

# Initialize services
if API_KEY:
    genai.configure(api_key=API_KEY)
    print("✅ Gemini API configured")
else:
    print("❌ Gemini API not configured")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized")
else:
    supabase = None
    print("❌ Supabase not configured")

# --- ENHANCED PROMPT BUILDER IMPORT ---
try:
    from utils.prompt_builder import build_enhanced_2025_prompt
    ENHANCED_PROMPT_AVAILABLE = True
    print("✅ Enhanced 2025 prompt builder imported")
except ImportError:
    ENHANCED_PROMPT_AVAILABLE = False
    print("⚠️ Enhanced prompt builder not available, using standard prompt")

# --- SCRAPER IMPORTS ---
try:
    from scrapers.check_https import check_https
    from scrapers.whois_sraper import get_whois_data
    from scrapers.check_privacy_term import check_privacy_term
    from scrapers.check_linkedin import check_social_presence
    from scrapers.google_safe_browsing_scraper import scrape_google_safe_browsing
    from scrapers.tranco_list_scraper import scrape_tranco_list
    from scrapers.ssl_org_scraper import scrape_ssl_org
    from scrapers.ipvoid_scraper import scrape_ipvoid
    from scrapers.mcc_classifier_gemini_final import classify_mcc_using_gemini, extract_text_from_url
    SCRAPERS_AVAILABLE = True
    print("✅ Scrapers imported successfully")
except ImportError as e:
    SCRAPERS_AVAILABLE = False
    print(f"⚠️ Scrapers not available: {e}")

# --- OFAC SCRAPER IMPORT ---
try:
    from scrapers.ofac_sanctions_scraper import check_ofac_sanctions
    OFAC_AVAILABLE = True
    print("✅ OFAC sanctions scraper imported")
except ImportError:
    OFAC_AVAILABLE = False
    print("⚠️ OFAC sanctions scraper not available")

# --- UTILITY FUNCTIONS ---
def extract_json_from_response(text: str) -> dict:
    """Extract JSON from AI response text"""
    print("--- Attempting to extract clean JSON from response text ---")
    json_match = re.search(r'\{.*\}', text, re.DOTALL)

    if not json_match:
        print("--- ERROR: NO JSON OBJECT FOUND IN RESPONSE ---")
        raise ValueError("No JSON object could be found in the text from the assessment service.")

    json_str = json_match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"--- ERROR: FAILED TO PARSE THE EXTRACTED JSON ---")
        raise ValueError(f"The JSON data from the assessment service is malformed. Details: {e}")

def store_risk_assessment(company_name: str, data: dict):
    """Store assessment in Supabase database"""
    if not supabase:
        print("⚠️ Warning: Supabase not configured, assessment not stored")
        return
        
    try:
        print(f"--- Storing assessment for {company_name} in Supabase ---")
        supabase.table("risk_assessments").insert({
            "company_name": company_name,
            "domain": data.get("domain"),
            "assessment_type": data.get("assessment_type", "standard"),
            "risk_assessment_data": data
        }).execute()
        print(f"--- Successfully stored assessment for {company_name} ---")
    except Exception as e:
        print(f"--- ERROR: FAILED TO STORE DATA IN SUPABASE ---")
        raise HTTPException(status_code=500, detail=f"Failed to save assessment to the database: {e}")

def extract_company_name_from_domain(domain: str) -> str:
    """Extract company name from domain"""
    # Remove protocol and www
    clean_domain = re.sub(r'^https?://', '', domain)
    clean_domain = re.sub(r'^www\.', '', clean_domain)
    
    # Remove TLD
    name = re.sub(r'\.(com|org|net|io|co|ai|app|dev|in|uk|ca)$', '', clean_domain)
    
    # Handle subdomains
    parts = name.split('.')
    if len(parts) > 1:
        name = parts[-2]
    else:
        name = parts[0]
    
    # Clean and capitalize
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    return name.capitalize()

# --- SCRAPER COORDINATION ---
def run_scraper_safely(scraper_func, *args, **kwargs) -> Dict:
    """Run scraper with error handling"""
    scraper_name = scraper_func.__name__
    try:
        print(f"🕷️ Running {scraper_name}...")
        result = scraper_func(*args, **kwargs)
        print(f"✅ {scraper_name} completed")
        return result if result else {}
    except Exception as e:
        print(f"❌ {scraper_name} failed: {e}")
        return {"error": str(e), "scraper": scraper_name}

def collect_enhanced_data(domain: str, assessment_type: str = "enhanced") -> Dict:
    """Collect data from available scrapers including OFAC"""
    if not SCRAPERS_AVAILABLE or assessment_type == "standard":
        return {}
    
    print(f"🕷️ Collecting enhanced data for: {domain}")
    scraped_data = {
        "collection_timestamp": datetime.now().isoformat(),
        "domain": domain
    }
    
    # Define priority scrapers
    priority_scrapers = [
        ("https_check", check_https),
        ("privacy_terms", check_privacy_term),
        ("whois_data", get_whois_data),
        ("social_presence", check_social_presence)
    ]
    
    # Add OFAC if available
    if OFAC_AVAILABLE:
        company_name = extract_company_name_from_domain(domain)
        priority_scrapers.append(("ofac_sanctions", lambda d: check_ofac_sanctions(company_name, d)))
    
    secondary_scrapers = [
        ("google_safe_browsing", scrape_google_safe_browsing),
        ("ssl_org_report", scrape_ssl_org),
        ("tranco_ranking", scrape_tranco_list)
    ]
    
    # Run priority scrapers first
    for scraper_name, scraper_func in priority_scrapers:
        scraped_data[scraper_name] = run_scraper_safely(scraper_func, domain)
        time.sleep(0.5)  # Rate limiting
    
    # Run secondary scrapers
    for scraper_name, scraper_func in secondary_scrapers:
        scraped_data[scraper_name] = run_scraper_safely(scraper_func, domain)
        time.sleep(0.5)  # Rate limiting
    
    # Industry classification
    try:
        website_url = f"https://{domain}"
        website_content = extract_text_from_url(website_url)
        if website_content and not website_content.startswith("Failed"):
            mcc_result = classify_mcc_using_gemini(domain, website_content[:1000])
            scraped_data["industry_classification"] = mcc_result
    except Exception as e:
        print(f"⚠️ Industry classification failed: {e}")
        scraped_data["industry_classification"] = {"error": str(e)}
    
    print(f"✅ Enhanced data collection completed: {len(scraped_data)} sources")
    return scraped_data

# --- ENHANCED PROMPT BUILDER ---
def build_enhanced_kyb_prompt(company_name: str, domain: str = None, scraped_data: Dict = None) -> str:
    """Build enhanced KYB prompt with 2025 compliance standards"""
    
    # Try to use enhanced prompt builder if available
    if ENHANCED_PROMPT_AVAILABLE and scraped_data:
        try:
            # Determine industry category from scraped data
            industry_data = scraped_data.get('industry_classification', {})
            if isinstance(industry_data, dict):
                industry_category = industry_data.get('industry_category', 'other')
                if not industry_category or industry_category == 'unknown':
                    # Try to get from MCC classification
                    mcc_code = industry_data.get('mcc_code', '')
                    if mcc_code:
                        industry_category = 'software_saas'  # Default mapping
                    else:
                        industry_category = 'other'
            else:
                industry_category = 'other'
            
            print(f"🔥 Using enhanced 2025 prompt for {company_name} (Industry: {industry_category})")
            return build_enhanced_2025_prompt(company_name, domain, industry_category, scraped_data)
            
        except Exception as e:
            print(f"⚠️ Enhanced prompt failed, falling back to standard: {e}")
    
    # Fallback to standard prompt
    return build_standard_kyb_prompt(company_name, domain, scraped_data)

def build_standard_kyb_prompt(company_name: str, domain: str = None, scraped_data: Dict = None) -> str:
    """Build standard KYB prompt (fallback)"""
    
    # Format scraped data if available
    scraped_context = ""
    if scraped_data and len(scraped_data) > 2:  # More than just timestamp and domain
        scraped_context = f"""

## REAL-TIME SCRAPED DATA ANALYSIS:
{format_scraped_data_for_prompt(scraped_data)}

## ENHANCED ASSESSMENT INSTRUCTIONS:
- Use the REAL scraped data above as PRIMARY evidence for scoring
- Cross-reference multiple sources when available
- If scraped data conflicts with general knowledge, TRUST the scraped data
- Assign confidence levels based on actual data availability and quality
"""
    
    domain_info = f" (Domain: {domain})" if domain else ""
    assessment_type = "enhanced_with_scrapers" if scraped_data else "standard"
    
    standard_prompt = f"""
# COMPREHENSIVE KYB RISK ASSESSMENT FOR CHARGEBEE
## Company: {company_name}{domain_info}
## Assessment Type: {assessment_type}

You are an expert KYB (Know Your Business) analyst for Chargebee, conducting a comprehensive risk assessment.

{scraped_context}

## ASSESSMENT FRAMEWORK (5 Risk Categories):

### 1. REPUTATION RISK (25%)
- Customer Reviews & Sentiment Analysis
- Social Media Presence Analysis
- Industry Reputation Assessment
- Executive Team Reputation

### 2. FINANCIAL RISK (25%)
- Financial Stability Analysis
- SEC Filings & Regulatory Disclosures
- Credit Risk Assessment
- Investment & Funding History

### 3. TECHNOLOGY RISK (20%)
- SSL/HTTPS Security Implementation
- Domain & Infrastructure Security
- Cybersecurity Incident History
- Data Protection Compliance

### 4. BUSINESS RISK (15%)
- Business Legitimacy Verification
- Market Position & Competitive Analysis
- Management Team Expertise

### 5. LEGAL COMPLIANCE RISK (15%)
- Regulatory Compliance History
- Litigation & Legal Disputes
- Privacy Policy & Legal Documentation

Return ONLY valid JSON in this exact structure:

{{
  "company_name": "{company_name}",
  "domain": "{domain}",
  "assessment_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "assessment_type": "{assessment_type}",
  "risk_categories": {{
    "reputation_risk": {{
      "checks": [
        {{
          "check_name": "Customer Reviews & Sentiment Analysis",
          "score": 0,
          "reason": "Detailed analysis based on available data",
          "insight": "Key findings and implications",
          "source": "Data sources used for this assessment",
          "public_data_available": true,
          "confidence_level": "high"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.25,
      "category_risk_level": "Medium"
    }},
    "financial_risk": {{
      "checks": [
        {{
          "check_name": "Financial Stability Analysis",
          "score": 0,
          "reason": "Revenue, profitability, and growth assessment",
          "insight": "Financial health indicators",
          "source": "Financial disclosures and market data",
          "public_data_available": true,
          "confidence_level": "medium"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.25,
      "category_risk_level": "Medium"
    }},
    "technology_risk": {{
      "checks": [
        {{
          "check_name": "SSL/HTTPS Security Implementation",
          "score": 0,
          "reason": "Website security and encryption analysis",
          "insight": "Technical security posture",
          "source": "SSL Labs and security scanners",
          "public_data_available": true,
          "confidence_level": "high"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.20,
      "category_risk_level": "Medium"
    }},
    "business_risk": {{
      "checks": [
        {{
          "check_name": "Business Legitimacy Verification",
          "score": 0,
          "reason": "Business registration and operational verification",
          "insight": "Operational legitimacy assessment",
          "source": "Business registries and operational data",
          "public_data_available": true,
          "confidence_level": "high"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.15,
      "category_risk_level": "Medium"
    }},
    "legal_compliance_risk": {{
      "checks": [
        {{
          "check_name": "Regulatory Compliance History",
          "score": 0,
          "reason": "Regulatory violations and enforcement actions",
          "insight": "Compliance track record",
          "source": "Regulatory databases and enforcement records",
          "public_data_available": true,
          "confidence_level": "medium"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.15,
      "category_risk_level": "Medium"
    }}
  }},
  "weighted_total_score": 0.0,
  "risk_level": "Medium",
  "confidence_score": 0.75,
  "metadata": {{
    "processing_time_seconds": 0,
    "data_sources_count": 0,
    "scraped_data_available": false,
    "assessment_version": "standard_v1.0"
  }}
}}
"""
    return standard_prompt

def format_scraped_data_for_prompt(scraped_data: Dict) -> str:
    """Format scraped data for inclusion in prompt"""
    if not scraped_data:
        return "No scraped data available"
    
    formatted_sections = []
    
    for source, data in scraped_data.items():
        if source in ["collection_timestamp", "domain"]:
            continue
            
        if isinstance(data, dict) and "error" not in data:
            section = f"**{source.replace('_', ' ').title()}:**\n"
            
            if source == "https_check":
                section += f"  - HTTPS Support: {data.get('has_https', 'Unknown')}\n"
                section += f"  - Protocol: {data.get('protocol', 'Unknown')}\n"
                
            elif source == "privacy_terms":
                section += f"  - Privacy Policy: {data.get('privacy_policy_present', 'Unknown')}\n"
                section += f"  - Terms of Service: {data.get('terms_of_service_present', 'Unknown')}\n"
                
            elif source == "whois_data":
                section += f"  - Creation Date: {data.get('creation_date', 'Unknown')}\n"
                section += f"  - Registrar: {data.get('registrar', 'Unknown')}\n"
                section += f"  - Expiration: {data.get('expiration_date', 'Unknown')}\n"
                
            elif source == "social_presence":
                if isinstance(data, str):
                    try:
                        social_data = json.loads(data)
                    except:
                        social_data = {}
                else:
                    social_data = data
                linkedin = social_data.get('social_presence', {}).get('linkedin', {})
                section += f"  - LinkedIn Presence: {linkedin.get('presence', 'Unknown')}\n"
                section += f"  - Employee Count: {social_data.get('employee_count', 'Unknown')}\n"
                
            elif source == "google_safe_browsing":
                section += f"  - Security Status: {data.get('Current Status', 'Unknown')}\n"
                
            elif source == "ssl_org_report":
                ssl_summary = data.get('report_summary', {})
                section += f"  - SSL Grade: {ssl_summary.get('ssl_grade', 'Unknown')}\n"
                
            elif source == "tranco_ranking":
                section += f"  - Tranco Rank: {data.get('Tranco Rank', 'Unknown')}\n"
                
            elif source == "industry_classification":
                section += f"  - MCC Code: {data.get('mcc_code', 'Unknown')}\n"
                section += f"  - Industry: {data.get('description', 'Unknown')}\n"
                section += f"  - Confidence: {data.get('confidence', 'Unknown')}\n"
                
            elif source == "ofac_sanctions":
                sanctions = data.get('sanctions_screening', {})
                section += f"  - OFAC Status: {sanctions.get('status', 'Unknown')}\n"
                section += f"  - Risk Level: {sanctions.get('risk_level', 'Unknown')}\n"
                section += f"  - Matches Found: {sanctions.get('total_matches', 0)}\n"
                
            else:
                # Generic formatting for other sources
                section += f"  - Data: Available\n"
            
            formatted_sections.append(section)
    
    return "\n".join(formatted_sections)

# --- MAIN ASSESSMENT FUNCTIONS ---
def get_risk_assessment(company_name: str, assessment_type: str = "standard") -> dict:
    """
    MAIN ASSESSMENT FUNCTION - Enhanced version
    
    Args:
        company_name: Company name or domain
        assessment_type: "standard" or "enhanced"
    """
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Assessment service not available - API key missing")
    
    start_time = time.time()
    
    try:
        print(f"--- Starting {assessment_type} risk assessment for: {company_name} ---")
        
        # Determine if input is domain or company name
        is_domain = "." in company_name and not company_name.startswith("http")
        
        if is_domain:
            domain = company_name
            company_name = extract_company_name_from_domain(domain)
        else:
            domain = f"{company_name.lower().replace(' ', '')}.com"
        
        print(f"--- Company: {company_name}, Domain: {domain} ---")
        
        # Collect enhanced data if requested
        scraped_data = {}
        if assessment_type == "enhanced" and SCRAPERS_AVAILABLE:
            scraped_data = collect_enhanced_data(domain, assessment_type)
        
        # Build enhanced prompt
        prompt = build_enhanced_kyb_prompt(company_name, domain, scraped_data)
        
        # Generate assessment
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Extract and validate JSON
        json_response = extract_json_from_response(response.text)
        
        # Add processing metadata
        processing_time = round(time.time() - start_time, 2)
        json_response.update({
            "company_name": company_name,
            "domain": domain,
            "assessment_date": datetime.now().strftime('%Y-%m-%d'),
            "assessment_type": assessment_type,
            "metadata": {
                "processing_time_seconds": processing_time,
                "data_sources_count": len(scraped_data) if scraped_data else 0,
                "scraped_data_available": bool(scraped_data),
                "assessment_version": "enhanced_v2.0" if ENHANCED_PROMPT_AVAILABLE else "standard_v1.0",
                "ofac_available": OFAC_AVAILABLE
            }
        })
        
        # Store in database
        store_risk_assessment(company_name, json_response)
        
        print(f"--- Assessment completed successfully for: {company_name} in {processing_time}s ---")
        return json_response
        
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Data processing error for {company_name}: {e}")
        raise HTTPException(status_code=502, detail=f"Assessment service returned invalid data: {e}")
    except Exception as e:
        print(f"Unexpected error for {company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {e}")

def get_enhanced_risk_assessment(domain: str) -> dict:
    """
    Enhanced assessment with real-time data collection
    This is the main function for domain-based enhanced assessments
    """
    return get_risk_assessment(domain, assessment_type="enhanced")

# --- UTILITY FUNCTIONS ---
def get_assessment_history(company_name: str) -> list:
    """Get assessment history for a company"""
    if not supabase:
        return []
        
    try:
        response = supabase.table("risk_assessments").select("*").eq("company_name", company_name).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching history for {company_name}: {e}")
        return []

def delete_assessment(assessment_id: str) -> bool:
    """Delete an assessment by ID"""
    if not supabase:
        return False
        
    try:
        supabase.table("risk_assessments").delete().eq("id", assessment_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting assessment {assessment_id}: {e}")
        return False

def get_assessment_by_domain(domain: str) -> dict:
    """Get most recent assessment for a domain"""
    if not supabase:
        return {}
        
    try:
        response = supabase.table("risk_assessments").select("*").eq("domain", domain).order("created_at", desc=True).limit(1).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        print(f"Error fetching assessment for domain {domain}: {e}")
        return {}

def get_system_health() -> dict:
    """Get system health status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini_api": "✅ Connected" if API_KEY else "❌ Not configured",
            "supabase": "✅ Connected" if supabase else "❌ Not configured",
            "scrapers": "✅ Available" if SCRAPERS_AVAILABLE else "⚠️ Limited functionality",
            "enhanced_prompt": "✅ Available" if ENHANCED_PROMPT_AVAILABLE else "⚠️ Standard prompt only",
            "ofac_screening": "✅ Available" if OFAC_AVAILABLE else "⚠️ Not available"
        },
        "capabilities": {
            "standard_assessment": True,
            "enhanced_assessment": SCRAPERS_AVAILABLE,
            "data_persistence": bool(supabase),
            "industry_classification": SCRAPERS_AVAILABLE,
            "sanctions_screening": OFAC_AVAILABLE,
            "compliance_2025": ENHANCED_PROMPT_AVAILABLE
        }
    }

# --- TEST FUNCTION ---
if __name__ == "__main__":
    # Test the enhanced assessment
    test_input = "shopify.com"
    print(f"Testing enhanced assessment for: {test_input}")
    
    try:
        # Test standard assessment
        print("\n=== STANDARD ASSESSMENT ===")
        standard_result = get_risk_assessment(test_input, "standard")
        print(f"✅ Standard assessment completed")
        print(f"Risk Level: {standard_result.get('risk_level', 'Unknown')}")
        print(f"Score: {standard_result.get('weighted_total_score', 0)}")
        
        # Test enhanced assessment if scrapers available
        if SCRAPERS_AVAILABLE:
            print("\n=== ENHANCED ASSESSMENT ===")
            enhanced_result = get_enhanced_risk_assessment(test_input)
            print(f"✅ Enhanced assessment completed")
            print(f"Risk Level: {enhanced_result.get('risk_level', 'Unknown')}")
            print(f"Score: {enhanced_result.get('weighted_total_score', 0)}")
            print(f"Data Sources: {enhanced_result.get('metadata', {}).get('data_sources_count', 0)}")
        
        # Test system health
        print("\n=== SYSTEM HEALTH ===")
        health = get_system_health()
        print(json.dumps(health, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")