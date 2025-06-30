# backend/utils/enhanced_prompt_builder.py
# ADD THIS FILE to your utils folder to enhance your existing prompt

import json
from typing import Dict, List, Optional
from datetime import datetime

def build_enhanced_2025_prompt(company_name: str, domain: str, industry_category: str, scraped_data: Dict) -> str:
    """
    Enhanced 2025 compliance prompt that integrates with your existing system
    This enhances your current prompt_builder.py with advanced compliance standards
    """
    
    # Build real-time data context from your scrapers
    real_time_context = build_scraped_data_context(scraped_data)
    
    # Get industry-specific intelligence
    industry_intel = get_industry_specific_requirements(industry_category)
    
    enhanced_prompt = f"""
You are conducting a comprehensive KYB (Know Your Business) risk assessment for {company_name} (Domain: {domain}) that meets 2025 enhanced due diligence standards for Chargebee.

{real_time_context}

## 🎯 2025 ENHANCED COMPLIANCE FRAMEWORK

### 1. REGULATORY COMPLIANCE RISK (30% Weight) - CRITICAL PRIORITY
**Ultimate Beneficial Owner (UBO) Analysis:**
- Identify all individuals with 25%+ ownership or control (EU/Global Standard)
- Map complete ownership structure including holding companies
- Flag complex or opaque ownership arrangements
- Assess transparency of beneficial ownership disclosure

**Sanctions & Watchlist Screening:**
- Screen against OFAC Specially Designated Nationals (SDN) list
- Cross-reference EU, UN, and other international sanctions
- Check for politically exposed persons (PEPs) in ownership/management
- Evaluate sanctions risk and compliance history

**Business Registration & Licensing:**
- Verify incorporation status with Secretary of State records
- Confirm business registration authenticity and current status
- Validate required industry-specific licenses and permits
- Check for regulatory compliance violations or enforcement actions

{industry_intel}

### 2. FINANCIAL TRANSPARENCY RISK (25% Weight)
**SEC/Financial Filings Analysis:**
- Review SEC EDGAR filings for public companies
- Analyze financial disclosures and transparency
- Assess ownership structure complexity
- Evaluate related party transactions and conflicts

**Capital Source Verification:**
- Assess legitimacy and source of business funding
- Review investment history and investor profiles
- Check for unexplained wealth or suspicious funding sources
- Evaluate financial sustainability and business model

### 3. OPERATIONAL LEGITIMACY RISK (20% Weight)
**Physical & Digital Presence:**
- Verify legitimate business address and physical operations
- Confirm website authenticity and business activity
- Assess employee count and organizational structure
- Validate operational substance vs. shell company indicators

**Business Activity Verification:**
- Confirm operations match stated business purpose
- Assess customer base legitimacy and geographic distribution
- Review supply chain and vendor relationships
- Evaluate business partnerships and professional networks

### 4. TECHNOLOGY SECURITY RISK (15% Weight)
**Cybersecurity & Data Protection:**
- Assess SSL/TLS implementation and security certificates
- Review data protection policies (GDPR, CCPA compliance)
- Evaluate cybersecurity posture and incident history
- Check for security certifications (SOC 2, ISO 27001)

### 5. REPUTATIONAL INTELLIGENCE RISK (10% Weight)
**Adverse Media & Public Perception:**
- Screen for negative news, investigations, or controversies
- Analyze social media presence and public sentiment
- Review customer complaints and business disputes
- Assess overall industry reputation and standing

## 📊 ENHANCED SCORING METHODOLOGY (2025 Standards)

### Scoring Scale (0-10 per check):
- **8-10**: Excellent - Strong compliance, low risk, transparent operations
- **6-7**: Good - Generally positive with minor concerns requiring monitoring
- **4-5**: Fair - Mixed indicators, moderate risk requiring enhanced due diligence
- **2-3**: Poor - Significant concerns, high risk requiring immediate attention
- **0-1**: Critical - Major red flags, very high risk, recommend rejection

### Critical Risk Multipliers:
- **Sanctions Matches**: Automatic 0 score for any category with matches
- **PEP Exposure**: Apply 1.5x penalty for high-risk political connections
- **Shell Company Indicators**: Apply 1.3x penalty for lack of substance
- **High-Risk Jurisdictions**: Apply 1.2x penalty for operations in sanctioned countries
- **Complex Ownership**: Apply 1.2x penalty for unclear beneficial ownership

### Data Quality Weighting:
- **High-confidence data** (government sources, verified records): Full weight
- **Medium-confidence data** (commercial databases, third-party): 0.8x weight  
- **Low-confidence data** (unverified sources, social media): 0.5x weight

## 🔍 CROSS-VALIDATION REQUIREMENTS

Use the real-time scraped data as PRIMARY evidence. Cross-reference findings across multiple sources. Flag any inconsistencies between:
- Business registration vs. operational reality
- Stated ownership vs. actual control
- Public statements vs. regulatory filings
- Online presence vs. physical operations

## 📋 REQUIRED JSON OUTPUT STRUCTURE

Return ONLY valid JSON in this exact format:

{{
  "company_name": "{company_name}",
  "domain": "{domain}",
  "assessment_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "assessment_type": "enhanced_2025_compliance",
  "industry_category": "{industry_category}",
  "compliance_version": "2025.1",
  
  "risk_categories": {{
    "regulatory_compliance_risk": {{
      "checks": [
        {{
          "check_name": "UBO Identification & Verification",
          "score": 0,
          "reason": "Analysis of beneficial ownership transparency based on available data",
          "insight": "Key findings about ownership structure and transparency",
          "source": "Corporate registries, Secretary of State records, business filings",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "25% ownership threshold analysis per 2025 standards"
        }},
        {{
          "check_name": "Sanctions & Watchlist Screening",
          "score": 0,
          "reason": "OFAC, EU, UN sanctions screening results for entity and beneficial owners",
          "insight": "Sanctions compliance status and risk assessment",
          "source": "OFAC SDN list, EU consolidated list, UN sanctions database",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Comprehensive sanctions screening completed"
        }},
        {{
          "check_name": "Business Registration & Licensing",
          "score": 0,
          "reason": "Corporate registration status and licensing compliance verification",
          "insight": "Legal entity standing and regulatory compliance",
          "source": "Secretary of State databases, business registration authorities",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Business registration authenticity verified"
        }},
        {{
          "check_name": "Industry-Specific Compliance",
          "score": 0,
          "reason": "Sector-specific regulatory requirements and compliance history",
          "insight": "Industry regulation adherence assessment",
          "source": "Industry regulators, licensing authorities, compliance databases",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Industry-specific requirements evaluated"
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
          "check_name": "Ownership Structure Complexity",
          "score": 0,
          "reason": "Corporate structure analysis for transparency and legitimacy",
          "insight": "Ownership structure risk evaluation",
          "source": "Corporate filings, beneficial ownership records",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Corporate structure complexity evaluated"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.25,
      "category_risk_level": "Medium"
    }},
    
    "operational_legitimacy_risk": {{
      "checks": [
        {{
          "check_name": "Business Substance Verification",
          "score": 0,
          "reason": "Physical presence and operational reality assessment",
          "insight": "Business legitimacy and operational substance evaluation",
          "source": "Address verification, business directories, operational data",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": [],
          "compliance_notes": "Operational substance verified against shell company indicators"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.20,
      "category_risk_level": "Medium"
    }},
    
    "technology_security_risk": {{
      "checks": [
        {{
          "check_name": "Cybersecurity & Data Protection",
          "score": 0,
          "reason": "Security controls, certifications, and data protection compliance",
          "insight": "Technology security posture assessment",
          "source": "Security certifications, SSL analysis, privacy policy review",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Security measures and data protection evaluated"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.15,
      "category_risk_level": "Medium"
    }},
    
    "reputational_intelligence_risk": {{
      "checks": [
        {{
          "check_name": "Adverse Media & Reputation Screening",
          "score": 0,
          "reason": "Negative news screening and reputation analysis",
          "insight": "Public reputation and media coverage assessment",
          "source": "News databases, media monitoring, public records",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": [],
          "compliance_notes": "Comprehensive adverse media screening completed"
        }}
      ],
      "average_score": 0.0,
      "weight": 0.10,
      "category_risk_level": "Medium"
    }}
  }},
  
  "weighted_total_score": 0.0,
  "risk_level": "Medium",
  "overall_confidence": 0.75,
  
  "enhanced_metadata": {{
    "ubo_identified": false,
    "sanctions_clear": true,
    "pep_exposure": false,
    "high_risk_jurisdiction": false,
    "enhanced_due_diligence_required": false,
    "shell_company_indicators": 0,
    "compliance_concerns": [],
    "data_sources_count": 0,
    "assessment_timestamp": "{datetime.now().isoformat()}",
    "compliance_version": "2025.1"
  }},
  
  "recommendations": {{
    "immediate_actions": [],
    "enhanced_monitoring": [],
    "compliance_requirements": [],
    "risk_mitigation": [],
    "approval_status": "pending_review"
  }}
}}

CRITICAL: Base your analysis strictly on the provided real-time data. Use the scraped data as PRIMARY evidence for all scores and findings. If critical information is missing, clearly state what additional data is needed for complete 2025 compliance assessment.
"""
    
    return enhanced_prompt

def build_scraped_data_context(scraped_data: Dict) -> str:
    """Format your existing scraped data for the enhanced prompt"""
    if not scraped_data:
        return "## 📊 REAL-TIME DATA: No scraped data available - assessment based on publicly available information"
    
    context = "## 📊 REAL-TIME SCRAPED DATA ANALYSIS:\n"
    
    # Process your existing scrapers
    security_findings = []
    business_findings = []
    compliance_findings = []
    
    for source, data in scraped_data.items():
        if source in ["collection_timestamp", "domain", "industry_category"]:
            continue
            
        if isinstance(data, dict) and "error" not in data:
            formatted_item = format_scraper_data(source, data)
            if formatted_item:
                if source in ["google_safe_browsing", "ssl_org_report", "ipvoid", "nordvpn_malicious"]:
                    security_findings.append(formatted_item)
                elif source in ["whois_data", "social_presence", "traffic_volume", "tranco_ranking"]:
                    business_findings.append(formatted_item)
                elif source in ["privacy_terms", "ofac_sanctions"]:
                    compliance_findings.append(formatted_item)
    
    if security_findings:
        context += "\n### 🔒 SECURITY INTELLIGENCE:\n" + "\n".join(security_findings)
    if business_findings:
        context += "\n### 🏢 BUSINESS INTELLIGENCE:\n" + "\n".join(business_findings)
    if compliance_findings:
        context += "\n### ⚖️ COMPLIANCE DATA:\n" + "\n".join(compliance_findings)
    
    context += f"\n\n**Data Collection Timestamp**: {scraped_data.get('collection_timestamp', 'Unknown')}"
    context += f"\n**Sources Analyzed**: {len([k for k in scraped_data.keys() if not k.startswith('collection_')])}"
    
    return context

def format_scraper_data(source: str, data: Dict) -> str:
    """Format individual scraper results for prompt context"""
    if source == "ofac_sanctions":
        sanctions = data.get('sanctions_screening', {})
        status = sanctions.get('status', 'UNKNOWN')
        matches = sanctions.get('total_matches', 0)
        return f"- **OFAC Sanctions Screening**: Status: {status}, Matches: {matches}"
    elif source == "google_safe_browsing":
        status = data.get('Current Status', 'Unknown')
        return f"- **Google Safe Browsing**: {status}"
    elif source == "ssl_org_report":
        summary = data.get('report_summary', {})
        grade = summary.get('ssl_grade', 'Unknown')
        return f"- **SSL Security Grade**: {grade} (SSL Labs Assessment)"
    elif source == "whois_data":
        created = data.get('creation_date', 'Unknown')
        registrar = data.get('registrar', 'Unknown')
        return f"- **Domain Registration**: Created {created}, Registrar: {registrar}"
    elif source == "social_presence":
        try:
            if isinstance(data, str):
                social_data = json.loads(data)
            else:
                social_data = data
            linkedin = social_data.get('social_presence', {}).get('linkedin', {})
            employees = social_data.get('employee_count', 'Unknown')
            return f"- **LinkedIn Presence**: Active: {linkedin.get('presence', False)}, Employees: {employees}"
        except:
            return f"- **Social Presence**: Data available"
    elif source == "privacy_terms":
        privacy = data.get('privacy_policy_present', False)
        terms = data.get('terms_of_service_present', False)
        return f"- **Legal Documentation**: Privacy Policy: {privacy}, Terms of Service: {terms}"
    else:
        return f"- **{source.replace('_', ' ').title()}**: Data collected"

def get_industry_specific_requirements(industry_category: str) -> str:
    """Get industry-specific compliance requirements"""
    industry_requirements = {
        "fintech_financial": """
**FINTECH/FINANCIAL SECTOR ENHANCED REQUIREMENTS:**
- **Banking License Verification**: Check required financial services licenses
- **PCI DSS Compliance**: Payment card industry security requirements
- **Capital Adequacy**: Minimum capital and reserve requirements
- **AML/BSA Program**: Anti-money laundering controls assessment
- **Consumer Protection**: CFPB compliance and consumer safeguards
- **Data Security**: Enhanced cybersecurity and data protection standards
""",
        "ecommerce_retail": """
**E-COMMERCE/RETAIL SECTOR ENHANCED REQUIREMENTS:**
- **Merchant Account Verification**: Payment processing legitimacy
- **Consumer Protection**: Return policies and customer service standards
- **Product Safety**: Product liability and safety compliance
- **Tax Compliance**: Sales tax collection and remittance verification
- **Supply Chain**: Vendor and supplier relationship verification
- **Brand Protection**: Trademark and intellectual property compliance
""",
        "software_saas": """
**SOFTWARE/SaaS SECTOR ENHANCED REQUIREMENTS:**
- **Data Protection**: GDPR, CCPA, and global privacy compliance
- **Security Certifications**: SOC 2, ISO 27001 verification
- **API Security**: Secure integration and access controls
- **Intellectual Property**: Software licensing and IP protection
- **Service Level Agreements**: SLA compliance and availability standards
- **Third-Party Integrations**: Vendor security and compliance assessment
"""
    }
    
    return industry_requirements.get(industry_category, "")

# Integration function for your existing system
def integrate_enhanced_prompt_with_existing_system():
    """
    Instructions to integrate this with your existing risk_assessment.py:
    
    1. Replace your build_enhanced_kyb_prompt function in risk_assessment.py with:
    
    from utils.enhanced_prompt_builder import build_enhanced_2025_prompt
    
    def build_enhanced_kyb_prompt(company_name: str, domain: str = None, scraped_data: Dict = None) -> str:
        # Determine industry category from scraped data
        industry_data = scraped_data.get('industry_classification', {}) if scraped_data else {}
        if isinstance(industry_data, dict):
            industry_category = industry_data.get('industry_category', 'software_saas')
        else:
            industry_category = 'software_saas'
        
        # Use enhanced 2025 prompt
        return build_enhanced_2025_prompt(company_name, domain, industry_category, scraped_data)
    
    2. This will enhance your existing system with 2025 compliance standards
    3. All your existing scrapers will work with the enhanced prompt
    4. The enhanced prompt will provide better UBO detection, sanctions screening, and compliance analysis
    """
    pass