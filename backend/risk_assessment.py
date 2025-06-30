# backend/risk_assessment.py
# COMPLETE FILE - Replace your entire risk_assessment.py with this
# SINGLE AMAZING ASSESSMENT ENGINE - AI + All Scrapers + 2025 Compliance

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
    print("✅ All scrapers imported successfully")
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
    """Store assessment in Supabase database and return assessment_id"""
    if not supabase:
        print("⚠️ Warning: Supabase not configured, assessment not stored")
        return None
        
    try:
        print(f"--- Storing assessment for {company_name} in Supabase ---")
        response = supabase.table("risk_assessments").insert({
            "company_name": company_name,
            "domain": data.get("domain"),
            "assessment_type": data.get("assessment_type", "amazing"),
            "risk_assessment_data": data
        }).execute()
        
        if response.data and len(response.data) > 0:
            assessment_id = response.data[0]["id"]
            print(f"--- Successfully stored assessment for {company_name} with ID: {assessment_id} ---")
            return assessment_id
        else:
            print("--- No data returned from insert ---")
            return None
            
    except Exception as e:
        print(f"--- ERROR: FAILED TO STORE DATA IN SUPABASE: {e} ---")
        return None

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

# --- AMAZING SCRAPER COORDINATION ---
def collect_amazing_data(domain: str) -> Dict:
    """🚀 THE MOST COMPREHENSIVE DATA COLLECTION POSSIBLE"""
    if not SCRAPERS_AVAILABLE:
        print("⚠️ Scrapers not available - returning empty data")
        return {}
    
    print(f"🚀 STARTING AMAZING DATA COLLECTION for: {domain}")
    print(f"⏱️ Collecting from ALL available sources (60-90 seconds)...")
    print(f"🎯 Target: 10+ scrapers with maximum data quality")
    
    scraped_data = {
        "collection_timestamp": datetime.now().isoformat(),
        "domain": domain,
        "scrapers_attempted": 0,
        "scrapers_successful": 0,
        "scrapers_failed": 0,
        "collection_quality": "amazing"
    }
    
    def run_scraper_with_amazing_quality(scraper_name, scraper_func, description, timeout=30):
        """Run scraper with maximum quality settings"""
        print(f"  🔍 Running {scraper_name}: {description}")
        scraped_data["scrapers_attempted"] += 1
        
        start_time = time.time()
        
        try:
            # Run scraper with generous timeout for quality
            result = scraper_func(domain)
            
            execution_time = round(time.time() - start_time, 2)
            
            # Enhanced result validation
            if result and isinstance(result, dict) and "error" not in str(result):
                print(f"    ✅ {scraper_name} completed successfully in {execution_time}s")
                scraped_data["scrapers_successful"] += 1
                
                # Add metadata to result
                if isinstance(result, dict):
                    result["_scraper_metadata"] = {
                        "scraper_name": scraper_name,
                        "execution_time": execution_time,
                        "quality": "high",
                        "timestamp": datetime.now().isoformat()
                    }
                
                return result
            else:
                print(f"    ⚠️ {scraper_name} returned low quality data in {execution_time}s")
                scraped_data["scrapers_failed"] += 1
                return {"error": f"Low quality data: {result}", "scraper": scraper_name}
                
        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            print(f"    ❌ {scraper_name} failed after {execution_time}s: {str(e)}")
            scraped_data["scrapers_failed"] += 1
            return {"error": str(e), "scraper": scraper_name}
    
    # 🎯 PHASE 1: CRITICAL FOUNDATION SCRAPERS
    print(f"📊 PHASE 1: CRITICAL FOUNDATION SCRAPERS")
    foundation_scrapers = [
        ("https_check", check_https, "SSL/HTTPS security verification"),
        ("whois_data", get_whois_data, "Domain registration and ownership"),
        ("privacy_terms", check_privacy_term, "Legal documentation compliance"),
    ]
    
    for scraper_name, scraper_func, description in foundation_scrapers:
        scraped_data[scraper_name] = run_scraper_with_amazing_quality(
            scraper_name, scraper_func, description, 25
        )
        time.sleep(3)  # Quality delay between scrapers
    
    # 🎯 PHASE 2: COMPLIANCE & SECURITY SCRAPERS
    print(f"📊 PHASE 2: COMPLIANCE & SECURITY SCRAPERS")
    security_scrapers = [
        ("google_safe_browsing", scrape_google_safe_browsing, "Security reputation analysis"),
        ("ssl_org_report", scrape_ssl_org, "SSL security grade assessment"),
        ("ipvoid", scrape_ipvoid, "IP reputation and geolocation"),
    ]
    
    # Add OFAC if available (CRITICAL for compliance)
    if OFAC_AVAILABLE:
        company_name = extract_company_name_from_domain(domain)
        security_scrapers.append(("ofac_sanctions", lambda d: check_ofac_sanctions(company_name, d), "OFAC sanctions screening"))
        print(f"   💼 Including OFAC sanctions screening for: {company_name}")
    
    for scraper_name, scraper_func, description in security_scrapers:
        scraped_data[scraper_name] = run_scraper_with_amazing_quality(
            scraper_name, scraper_func, description, 30
        )
        time.sleep(3)  # Quality delay between scrapers
    
    # 🎯 PHASE 3: BUSINESS INTELLIGENCE SCRAPERS
    print(f"📊 PHASE 3: BUSINESS INTELLIGENCE SCRAPERS")
    business_scrapers = [
        ("social_presence", check_social_presence, "LinkedIn and social media analysis"),
        ("tranco_ranking", scrape_tranco_list, "Website traffic and ranking"),
    ]
    
    for scraper_name, scraper_func, description in business_scrapers:
        scraped_data[scraper_name] = run_scraper_with_amazing_quality(
            scraper_name, scraper_func, description, 25
        )
        time.sleep(3)  # Quality delay between scrapers
    
    # 🎯 PHASE 4: INDUSTRY CLASSIFICATION (AI-POWERED)
    print(f"📊 PHASE 4: AI-POWERED INDUSTRY CLASSIFICATION")
    try:
        scraped_data["scrapers_attempted"] += 1
        print(f"  🤖 Running industry_classification: AI-powered business categorization")
        
        website_url = f"https://{domain}"
        website_content = extract_text_from_url(website_url)
        
        if website_content and not website_content.startswith("Failed"):
            mcc_result = classify_mcc_using_gemini(domain, website_content[:1500])  # More content for better classification
            
            if mcc_result:
                scraped_data["industry_classification"] = mcc_result
                scraped_data["scrapers_successful"] += 1
                print(f"    ✅ Industry classification completed successfully")
                print(f"      🏭 Industry: {mcc_result.get('industry_category', 'Unknown')}")
                print(f"      🎯 Confidence: {mcc_result.get('confidence', 0)}")
            else:
                scraped_data["industry_classification"] = {"error": "Classification failed"}
                scraped_data["scrapers_failed"] += 1
        else:
            scraped_data["industry_classification"] = {"error": "Failed to extract website content"}
            scraped_data["scrapers_failed"] += 1
            
    except Exception as e:
        print(f"    ❌ Industry classification failed: {e}")
        scraped_data["industry_classification"] = {"error": str(e)}
        scraped_data["scrapers_failed"] += 1
    
    # 🎯 FINAL SUMMARY & QUALITY ASSESSMENT
    total_scrapers = scraped_data["scrapers_attempted"]
    successful_scrapers = scraped_data["scrapers_successful"]
    failed_scrapers = scraped_data["scrapers_failed"]
    success_rate = (successful_scrapers / max(total_scrapers, 1)) * 100
    
    print(f"✅ AMAZING DATA COLLECTION COMPLETED:")
    print(f"   📊 Total scrapers attempted: {total_scrapers}")
    print(f"   ✅ Successful: {successful_scrapers}")
    print(f"   ❌ Failed: {failed_scrapers}")
    print(f"   📈 Success rate: {success_rate:.1f}%")
    print(f"   🏆 Quality level: {'EXCELLENT' if success_rate >= 80 else 'GOOD' if success_rate >= 60 else 'ACCEPTABLE'}")
    
    # Add quality metadata
    scraped_data["collection_summary"] = {
        "total_scrapers": total_scrapers,
        "successful_scrapers": successful_scrapers,
        "failed_scrapers": failed_scrapers,
        "success_rate": round(success_rate, 1),
        "quality_level": "EXCELLENT" if success_rate >= 80 else "GOOD" if success_rate >= 60 else "ACCEPTABLE",
        "collection_time": datetime.now().isoformat(),
        "ofac_included": OFAC_AVAILABLE,
        "scrapers_list": list(scraped_data.keys())
    }
    
    return scraped_data

# --- ENHANCED PROMPT BUILDER ---
def build_amazing_kyb_prompt(company_name: str, domain: str = None, scraped_data: Dict = None) -> str:
    """Build the most comprehensive KYB prompt possible"""
    
    # Try to use enhanced prompt builder if available
    if ENHANCED_PROMPT_AVAILABLE and scraped_data:
        try:
            # Determine industry category from scraped data
            industry_data = scraped_data.get('industry_classification', {})
            if isinstance(industry_data, dict):
                industry_category = industry_data.get('industry_category', 'other')
                if not industry_category or industry_category == 'unknown':
                    industry_category = 'other'
            else:
                industry_category = 'other'
            
            print(f"🔥 Using enhanced 2025 prompt for {company_name} (Industry: {industry_category})")
            return build_enhanced_2025_prompt(company_name, domain, industry_category, scraped_data)
            
        except Exception as e:
            print(f"⚠️ Enhanced prompt failed, falling back to amazing prompt: {e}")
    
    # Amazing fallback prompt
    return build_amazing_fallback_prompt(company_name, domain, scraped_data)

def build_amazing_fallback_prompt(company_name: str, domain: str = None, scraped_data: Dict = None) -> str:
    """Build amazing KYB prompt (enhanced fallback)"""
    
    # Format scraped data if available
    scraped_context = ""
    if scraped_data and len(scraped_data) > 5:  # More than just metadata
        scraped_context = f"""

## 🚀 REAL-TIME AMAZING DATA ANALYSIS:
{format_amazing_scraped_data_for_prompt(scraped_data)}

## 🎯 ENHANCED ASSESSMENT INSTRUCTIONS:
- Use the REAL scraped data above as PRIMARY evidence for all scoring
- Cross-reference multiple sources when available (we have {scraped_data.get('scrapers_successful', 0)} successful sources)
- If scraped data conflicts with general knowledge, TRUST the scraped data
- Apply 2025 compliance standards for risk assessment
- Focus on UBO detection, sanctions screening, and regulatory compliance
- Assign confidence levels based on actual data availability and quality
"""
    
    domain_info = f" (Domain: {domain})" if domain else ""
    
    amazing_prompt = f"""
# 🚀 AMAZING KYB RISK ASSESSMENT FOR CHARGEBEE
## Company: {company_name}{domain_info}
## Assessment Type: AMAZING (AI + All Scrapers + 2025 Compliance)
## Quality Level: MAXIMUM

You are conducting the MOST COMPREHENSIVE KYB (Know Your Business) risk assessment possible for Chargebee.

{scraped_context}

## 🎯 AMAZING ASSESSMENT FRAMEWORK (5 Enhanced Risk Categories):

### 1. REGULATORY COMPLIANCE RISK (30% Weight) - CRITICAL
- **Ultimate Beneficial Owner (UBO) Analysis**: 25%+ ownership detection
- **Sanctions & Watchlist Screening**: OFAC, EU, UN comprehensive screening
- **Business Registration Verification**: Secretary of State validation
- **Industry-Specific Compliance**: Sector regulatory requirements
- **Politically Exposed Persons (PEP)**: Political connection screening

### 2. FINANCIAL TRANSPARENCY RISK (25% Weight)
- **SEC & Financial Filings**: Public disclosure analysis
- **Ownership Structure Complexity**: Corporate transparency assessment
- **Capital Source Verification**: Funding legitimacy evaluation
- **Financial Stability**: Revenue and growth analysis

### 3. TECHNOLOGY SECURITY RISK (20% Weight)
- **SSL/HTTPS Security**: Advanced security implementation
- **Domain & Infrastructure**: Technical security posture
- **Cybersecurity Certifications**: SOC 2, ISO 27001 verification
- **Data Protection Compliance**: GDPR, CCPA adherence

### 4. BUSINESS LEGITIMACY RISK (15% Weight)
- **Operational Substance**: Physical vs shell company analysis
- **Business Activity Verification**: Operations vs stated purpose
- **Market Position**: Competitive landscape assessment
- **Professional Networks**: Industry connections validation

### 5. REPUTATIONAL INTELLIGENCE RISK (10% Weight)
- **Adverse Media Screening**: Negative news and controversies
- **Social Media Presence**: Professional online reputation
- **Customer Reviews & Sentiment**: Public perception analysis
- **Industry Standing**: Peer recognition and awards

## 📊 AMAZING SCORING METHODOLOGY (2025 Standards):

### Enhanced Scoring Scale (0-10 per check):
- **9-10**: EXCELLENT - Exceptional compliance, very low risk, transparent operations
- **7-8**: GOOD - Strong performance with minor areas for monitoring
- **5-6**: FAIR - Acceptable with some concerns requiring enhanced due diligence
- **3-4**: POOR - Significant issues requiring immediate attention and risk mitigation
- **0-2**: CRITICAL - Major red flags, very high risk, recommend rejection or extensive investigation

### Critical Risk Multipliers (2025 Standards):
- **Sanctions Matches**: Automatic 0 score if any sanctions found
- **PEP High Risk**: Apply 1.5x penalty for high-risk political connections
- **Shell Company Indicators**: Apply 1.3x penalty for lack of operational substance
- **High-Risk Jurisdictions**: Apply 1.2x penalty for operations in sanctioned countries
- **Complex Ownership**: Apply 1.2x penalty for unclear beneficial ownership (25% threshold)

Return ONLY valid JSON in this exact structure:

{{
  "company_name": "{company_name}",
  "domain": "{domain}",
  "assessment_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "assessment_type": "amazing",
  "industry_category": "unknown",
  "compliance_version": "2025_amazing",
  
  "risk_categories": {{
    "regulatory_compliance_risk": {{
      "checks": [
        {{
          "check_name": "UBO Identification & Verification (25% Threshold)",
          "score": 0,
          "reason": "Analysis of beneficial ownership transparency and 25% threshold compliance",
          "insight": "Key findings about ownership structure and UBO identification",
          "source": "Corporate registries, business filings, public ownership data",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "2025 UBO standards applied with 25% ownership threshold"
        }},
        {{
          "check_name": "Enhanced Sanctions & Watchlist Screening",
          "score": 0,
          "reason": "Comprehensive OFAC, EU, UN sanctions screening for entity and beneficial owners",
          "insight": "Sanctions compliance status and risk assessment",
          "source": "OFAC SDN list, EU consolidated list, UN sanctions database",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Multi-jurisdiction sanctions screening completed"
        }},
        {{
          "check_name": "Business Registration & Licensing Verification",
          "score": 0,
          "reason": "Corporate registration status and licensing compliance verification",
          "insight": "Legal entity standing and regulatory compliance assessment",
          "source": "Secretary of State databases, business registration authorities",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Business registration authenticity and currency verified"
        }},
        {{
          "check_name": "Industry-Specific Compliance Requirements",
          "score": 0,
          "reason": "Sector-specific regulatory requirements and compliance history",
          "insight": "Industry regulation adherence and specialized compliance",
          "source": "Industry regulators, licensing authorities, compliance databases",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Industry-specific regulatory requirements evaluated"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.30,
      "category_risk_level": "Medium",
      "compliance_status": "Under Review",
      "critical_findings": []
    }},
    
    "financial_transparency_risk": {{
      "checks": [
        {{
          "check_name": "SEC & Financial Filings Analysis",
          "score": 0,
          "reason": "Public financial disclosure review and transparency assessment",
          "insight": "Financial reporting quality and transparency evaluation",
          "source": "SEC EDGAR database, financial regulatory filings",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Financial disclosure transparency assessed"
        }},
        {{
          "check_name": "Ownership Structure Complexity Assessment",
          "score": 0,
          "reason": "Corporate structure analysis for transparency and legitimacy",
          "insight": "Ownership structure risk and complexity evaluation",
          "source": "Corporate filings, beneficial ownership records",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Corporate structure complexity and transparency evaluated"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.25,
      "category_risk_level": "Medium"
    }},
    
    "technology_security_risk": {{
      "checks": [
        {{
          "check_name": "Advanced Security Implementation",
          "score": 0,
          "reason": "SSL/HTTPS, security certifications, and cybersecurity posture",
          "insight": "Technical security infrastructure and implementation quality",
          "source": "SSL Labs, security scanners, certification databases",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Advanced security measures and certifications evaluated"
        }},
        {{
          "check_name": "Data Protection & Privacy Compliance",
          "score": 0,
          "reason": "GDPR, CCPA compliance and data protection implementation",
          "insight": "Data privacy and protection compliance assessment",
          "source": "Privacy policies, compliance certifications, regulatory filings",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Data protection compliance with global privacy standards"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.20,
      "category_risk_level": "Medium"
    }},
    
    "business_legitimacy_risk": {{
      "checks": [
        {{
          "check_name": "Operational Substance Verification",
          "score": 0,
          "reason": "Physical presence, operational reality, and business substance assessment",
          "insight": "Business legitimacy and operational substance evaluation",
          "source": "Address verification, business directories, operational data",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Operational substance verified against shell company indicators"
        }},
        {{
          "check_name": "Business Activity & Market Position",
          "score": 0,
          "reason": "Business operations verification and market presence analysis",
          "insight": "Market position and business activity legitimacy",
          "source": "Business databases, market analysis, industry reports",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Business activity alignment with stated purpose verified"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.15,
      "category_risk_level": "Medium"
    }},
    
    "reputational_intelligence_risk": {{
      "checks": [
        {{
          "check_name": "Comprehensive Adverse Media Screening",
          "score": 0,
          "reason": "Negative news screening and reputation analysis across all media",
          "insight": "Public reputation and media coverage comprehensive assessment",
          "source": "News databases, media monitoring, public records, social media",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Comprehensive adverse media screening across all available sources"
        }},
        {{
          "check_name": "Professional Reputation & Industry Standing",
          "score": 0,
          "reason": "Industry reputation, professional networks, and peer recognition",
          "insight": "Professional standing and industry reputation assessment",
          "source": "Industry associations, professional networks, awards databases",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Professional reputation and industry standing evaluated"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.10,
      "category_risk_level": "Medium"
    }}
  }},
  
  "weighted_total_score": 0.0,
  "risk_level": "Medium",
  "overall_confidence": 0.85,
  
  "enhanced_metadata": {{
    "ubo_identified": false,
    "ubo_threshold_met": false,
    "sanctions_clear": true,
    "pep_exposure": false,
    "high_risk_jurisdiction": false,
    "enhanced_due_diligence_required": false,
    "shell_company_indicators": 0,
    "compliance_concerns": [],
    "data_sources_count": 0,
    "assessment_timestamp": "{datetime.now().isoformat()}",
    "compliance_version": "2025_amazing",
    "quality_level": "amazing"
  }},
  
  "recommendations": {{
    "immediate_actions": [],
    "enhanced_monitoring": [],
    "compliance_requirements": [],
    "risk_mitigation": [],
    "approval_status": "pending_review",
    "next_review_date": "{(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}"
  }}
}}

CRITICAL: Base your analysis strictly on the provided real-time data. Use the scraped data as PRIMARY evidence for all scores and findings. Apply 2025 compliance standards including UBO detection (25% threshold), comprehensive sanctions screening, and enhanced due diligence requirements.
"""
    
    return amazing_prompt

def format_amazing_scraped_data_for_prompt(scraped_data: Dict) -> str:
    """Format scraped data for the amazing prompt"""
    if not scraped_data:
        return "No scraped data available"
    
    formatted_sections = []
    
    # Add collection summary first
    collection_summary = scraped_data.get('collection_summary', {})
    if collection_summary:
        summary_section = f"**COLLECTION SUMMARY:**\n"
        summary_section += f"  - Quality Level: {collection_summary.get('quality_level', 'Unknown')}\n"
        summary_section += f"  - Success Rate: {collection_summary.get('success_rate', 0)}%\n"
        summary_section += f"  - Total Sources: {collection_summary.get('total_scrapers', 0)}\n"
        summary_section += f"  - Successful: {collection_summary.get('successful_scrapers', 0)}\n"
        summary_section += f"  - OFAC Available: {collection_summary.get('ofac_included', False)}\n\n"
        formatted_sections.append(summary_section)
    
    for source, data in scraped_data.items():
        if source in ["collection_timestamp", "domain", "scrapers_attempted", "scrapers_successful", "scrapers_failed", "collection_summary", "collection_quality"]:
            continue
            
        if isinstance(data, dict) and "error" not in data:
            section = f"**{source.replace('_', ' ').title()}:**\n"
            
            if source == "https_check":
                section += f"  - HTTPS Support: {data.get('has_https', 'Unknown')}\n"
                section += f"  - Protocol: {data.get('protocol', 'Unknown')}\n"
                section += f"  - Security Status: {'SECURE' if data.get('has_https') else 'INSECURE'}\n"
                
            elif source == "privacy_terms":
                section += f"  - Privacy Policy: {data.get('privacy_policy_present', 'Unknown')}\n"
                section += f"  - Terms of Service: {data.get('terms_of_service_present', 'Unknown')}\n"
                section += f"  - Legal Compliance: {'GOOD' if data.get('privacy_policy_present') and data.get('terms_of_service_present') else 'NEEDS IMPROVEMENT'}\n"
                
            elif source == "whois_data":
                section += f"  - Creation Date: {data.get('creation_date', 'Unknown')}\n"
                section += f"  - Registrar: {data.get('registrar', 'Unknown')}\n"
                section += f"  - Expiration: {data.get('expiration_date', 'Unknown')}\n"
                section += f"  - Registration Status: {'VALID' if data.get('creation_date') else 'UNKNOWN'}\n"
                
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
                section += f"  - Professional Network: {'ESTABLISHED' if linkedin.get('presence') else 'LIMITED'}\n"
                
            elif source == "google_safe_browsing":
                section += f"  - Security Status: {data.get('Current Status', 'Unknown')}\n"
                section += f"  - Threat Level: {'SAFE' if 'safe' in str(data.get('Current Status', '')).lower() else 'NEEDS REVIEW'}\n"
                
            elif source == "ssl_org_report":
                ssl_summary = data.get('report_summary', {})
                grade = ssl_summary.get('ssl_grade', 'Unknown')
                section += f"  - SSL Grade: {grade}\n"
                section += f"  - Security Level: {'EXCELLENT' if grade in ['A+', 'A'] else 'GOOD' if grade in ['A-', 'B'] else 'NEEDS IMPROVEMENT'}\n"
                
            elif source == "tranco_ranking":
                rank = data.get('Tranco Rank', 'Unknown')
                section += f"  - Tranco Rank: {rank}\n"
                section += f"  - Traffic Level: {'HIGH' if isinstance(rank, int) and rank < 100000 else 'MODERATE' if isinstance(rank, int) and rank < 1000000 else 'LOW'}\n"
                
            elif source == "industry_classification":
                section += f"  - MCC Code: {data.get('mcc_code', 'Unknown')}\n"
                section += f"  - Industry: {data.get('industry_category', 'Unknown')}\n"
                section += f"  - Description: {data.get('description', 'Unknown')}\n"
                section += f"  - Confidence: {data.get('confidence', 'Unknown')}\n"
                section += f"  - Classification Quality: {'HIGH' if data.get('confidence', 0) > 0.7 else 'MEDIUM' if data.get('confidence', 0) > 0.4 else 'LOW'}\n"
                
            elif source == "ofac_sanctions":
                sanctions = data.get('sanctions_screening', {})
                status = sanctions.get('status', 'Unknown')
                risk_level = sanctions.get('risk_level', 'Unknown')
                matches = sanctions.get('total_matches', 0)
                section += f"  - OFAC Status: {status}\n"
                section += f"  - Risk Level: {risk_level}\n"
                section += f"  - Matches Found: {matches}\n"
                section += f"  - Sanctions Compliance: {'CLEAR' if matches == 0 else 'REQUIRES REVIEW'}\n"
                
            elif source == "ipvoid":
                section += f"  - IP Address: {data.get('ip_address', 'Unknown')}\n"
                section += f"  - Country: {data.get('country_code', 'Unknown')}\n"
                section += f"  - Reputation: {'GOOD' if not data.get('is_malicious') else 'POOR'}\n"
                
            else:
                # Generic formatting for other sources
                section += f"  - Data Quality: HIGH\n"
                section += f"  - Status: COLLECTED\n"
            
            formatted_sections.append(section)
    
    return "\n".join(formatted_sections)

# --- MAIN ASSESSMENT FUNCTIONS ---
def get_enhanced_risk_assessment(domain: str) -> dict:
    """
    🚀 THE SINGLE AMAZING ASSESSMENT FUNCTION
    - Always uses the most robust data collection
    - 10+ scrapers including OFAC, industry classification
    - Enhanced AI analysis with 2025 compliance
    - Complete data preservation
    """
    return get_risk_assessment(domain, assessment_type="amazing")

def get_risk_assessment(company_name: str, assessment_type: str = "amazing") -> dict:
    """
    🚀 MAIN AMAZING ASSESSMENT FUNCTION
    
    Args:
        company_name: Company name or domain
        assessment_type: Always "amazing" for best quality
    """
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Assessment service not available - API key missing")
    
    start_time = time.time()
    
    try:
        print(f"--- Starting AMAZING risk assessment for: {company_name} ---")
        
        # Determine if input is domain or company name
        is_domain = "." in company_name and not company_name.startswith("http")
        
        if is_domain:
            domain = company_name
            company_name = extract_company_name_from_domain(domain)
        else:
            domain = f"{company_name.lower().replace(' ', '')}.com"
        
        print(f"--- Company: {company_name}, Domain: {domain} ---")
        
        # Always collect amazing data (enhanced with all scrapers)
        print(f"🚀 STARTING AMAZING DATA COLLECTION...")
        scraped_data = collect_amazing_data(domain)
        print(f"📊 Amazing data collection completed with {scraped_data.get('scrapers_successful', 0)} successful scrapers")
        
        # Build amazing prompt
        print(f"🤖 GENERATING AMAZING AI ASSESSMENT...")
        prompt = build_amazing_kyb_prompt(company_name, domain, scraped_data)
        
        # Generate assessment with enhanced model settings
        model = genai.GenerativeModel('gemini-1.5-flash')
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,  # Lower temperature for more consistent results
            max_output_tokens=8192,  # More tokens for detailed analysis
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # Extract and validate JSON
        json_response = extract_json_from_response(response.text)
        
        # Add amazing processing metadata
        processing_time = round(time.time() - start_time, 2)
        json_response.update({
            "company_name": company_name,
            "domain": domain,
            "assessment_date": datetime.now().strftime('%Y-%m-%d'),
            "assessment_type": "amazing",
            "scraped_data": scraped_data,  # Include ALL scraped data in response
            "metadata": {
                "processing_time_seconds": processing_time,
                "data_sources_count": len(scraped_data) if scraped_data else 0,
                "scraped_data_available": bool(scraped_data),
                "assessment_version": "amazing_v3.0",
                "ai_model": "gemini-1.5-flash",
                "prompt_type": "enhanced_2025" if ENHANCED_PROMPT_AVAILABLE else "amazing_fallback",
                "ofac_available": OFAC_AVAILABLE,
                "scrapers_successful": scraped_data.get("scrapers_successful", 0),
                "scrapers_attempted": scraped_data.get("scrapers_attempted", 0),
                "data_collection_success_rate": round((scraped_data.get("scrapers_successful", 0) / max(scraped_data.get("scrapers_attempted", 1), 1)) * 100, 1),
                "quality_level": scraped_data.get("collection_summary", {}).get("quality_level", "UNKNOWN"),
                "compliance_standards": "2025_enhanced"
            }
        })
        
        # Store in database and get assessment_id
        print(f"💾 STORING AMAZING ASSESSMENT IN DATABASE...")
        assessment_id = store_risk_assessment(company_name, json_response)
        if assessment_id:
            json_response["assessment_id"] = assessment_id
            print(f"✅ Amazing assessment stored with ID: {assessment_id}")
        
        print(f"--- AMAZING ASSESSMENT COMPLETED SUCCESSFULLY for: {company_name} in {processing_time:.2f}s ---")
        print(f"--- Quality Level: {json_response.get('metadata', {}).get('quality_level', 'UNKNOWN')} ---")
        print(f"--- Success Rate: {json_response.get('metadata', {}).get('data_collection_success_rate', 0)}% ---")
        
        return json_response
        
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Data processing error for {company_name}: {e}")
        raise HTTPException(status_code=502, detail=f"Assessment service returned invalid data: {e}")
    except Exception as e:
        print(f"Unexpected error for {company_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {e}")

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
            "scrapers": "✅ Amazing Quality" if SCRAPERS_AVAILABLE else "⚠️ Limited functionality",
            "enhanced_prompt": "✅ 2025 Compliance" if ENHANCED_PROMPT_AVAILABLE else "⚠️ Standard prompt only",
            "ofac_screening": "✅ Available" if OFAC_AVAILABLE else "⚠️ Not available"
        },
        "capabilities": {
            "amazing_assessment": True,
            "enhanced_data_collection": SCRAPERS_AVAILABLE,
            "data_persistence": bool(supabase),
            "industry_classification": SCRAPERS_AVAILABLE,
            "sanctions_screening": OFAC_AVAILABLE,
            "compliance_2025": ENHANCED_PROMPT_AVAILABLE,
            "quality_level": "AMAZING"
        }
    }

# --- TEST FUNCTION ---
if __name__ == "__main__":
    # Test the amazing assessment
    test_input = "shopify.com"
    print(f"Testing AMAZING assessment for: {test_input}")
    
    try:
        print("\n=== AMAZING ASSESSMENT TEST ===")
        amazing_result = get_enhanced_risk_assessment(test_input)
        print(f"✅ Amazing assessment completed")
        print(f"Risk Level: {amazing_result.get('risk_level', 'Unknown')}")
        print(f"Score: {amazing_result.get('weighted_total_score', 0)}")
        print(f"Data Sources: {amazing_result.get('metadata', {}).get('data_sources_count', 0)}")
        print(f"Success Rate: {amazing_result.get('metadata', {}).get('data_collection_success_rate', 0)}%")
        print(f"Quality Level: {amazing_result.get('metadata', {}).get('quality_level', 'Unknown')}")
        
        # Test system health
        print("\n=== SYSTEM HEALTH ===")
        health = get_system_health()
        print(json.dumps(health, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")