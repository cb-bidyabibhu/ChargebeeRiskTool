# backend/utils/enhanced_prompt_builder.py
# ENHANCED VERSION - Add this to your existing prompt_builder.py or replace it

import json
from typing import Dict, List, Optional
from datetime import datetime

class Enhanced2025PromptBuilder:
    """
    Enhanced prompt builder with 2025 compliance standards and real-time data integration
    """
    
    def __init__(self):
        self.base_template = self._load_enhanced_template()
        self.compliance_standards = self._load_2025_compliance_standards()
        self.industry_intelligence = self._load_industry_intelligence()
    
    def _load_enhanced_template(self) -> str:
        return """
You are conducting a comprehensive KYB (Know Your Business) risk assessment for {company_name} (Domain: {domain}) that meets 2025 enhanced due diligence standards.

{real_time_data_context}

{compliance_requirements_section}

{industry_specific_intelligence}

## 🔍 2025 ENHANCED ASSESSMENT FRAMEWORK

### 1. REGULATORY COMPLIANCE RISK (30% Weight)
**Enhanced Due Diligence Requirements:**
- **Ultimate Beneficial Owner (UBO) Analysis**: Identify individuals with 25%+ ownership/control
- **Sanctions & Watchlist Screening**: Cross-reference OFAC, EU, UN sanctions lists
- **PEP (Politically Exposed Persons) Screening**: Flag high-risk political connections
- **Business Registration Verification**: Confirm legitimate incorporation and licenses
- **Industry-Specific Compliance**: Verify sector-specific regulatory requirements
- **AML/CFT Assessment**: Evaluate anti-money laundering controls

### 2. FINANCIAL TRANSPARENCY RISK (25% Weight)
**Financial Intelligence Analysis:**
- **SEC/Regulatory Filings**: Analyze public financial disclosures
- **Ownership Structure**: Map complex corporate structures and beneficial ownership
- **Capital Source Verification**: Assess legitimacy of funding sources
- **Financial Stability**: Evaluate creditworthiness and financial health
- **Related Party Transactions**: Identify potential conflicts of interest

### 3. OPERATIONAL LEGITIMACY RISK (20% Weight)
**Business Verification:**
- **Physical Presence**: Verify legitimate business address and operations
- **Employee Verification**: Confirm actual workforce and organizational structure
- **Business Activity**: Validate operations match stated business purpose
- **Customer Base**: Assess legitimacy of customer relationships
- **Supply Chain**: Verify business partnerships and vendor relationships

### 4. TECHNOLOGY SECURITY RISK (15% Weight)
**Cybersecurity & Data Protection:**
- **Security Posture**: Assess cybersecurity controls and certifications
- **Data Protection**: Verify GDPR, CCPA, and privacy compliance
- **Infrastructure Security**: Evaluate technical security measures
- **Third-Party Risk**: Assess vendor and integration security
- **Incident History**: Review past security breaches and response

### 5. REPUTATIONAL INTELLIGENCE RISK (10% Weight)
**Public Perception & Media Analysis:**
- **Adverse Media**: Screen for negative news and investigations
- **Social Media Intelligence**: Analyze public sentiment and presence
- **Customer Satisfaction**: Evaluate reviews and customer feedback
- **Industry Standing**: Assess reputation within business sector

{enhanced_scoring_instructions}

{cross_validation_requirements}

{json_output_structure}
"""
    
    def _load_2025_compliance_standards(self) -> str:
        return """
## 🛡️ 2025 COMPLIANCE STANDARDS

### Critical Screening Requirements:
1. **OFAC Sanctions Screening**: Mandatory for all entities and beneficial owners
2. **PEP Database Screening**: Screen against global PEP databases
3. **Adverse Media Monitoring**: Comprehensive negative news screening
4. **UBO Identification**: 25% ownership threshold per global standards
5. **Enhanced Due Diligence**: Risk-based approach with additional verification

### Red Flag Indicators:
- Complex ownership structures with multiple jurisdictions
- Recent incorporation with immediate high-value transactions
- Beneficial owners in high-risk countries
- Lack of legitimate business operations
- Inconsistent business information across sources
- Connections to sanctioned entities or PEPs
- Significant adverse media coverage
- Shell company characteristics

### Documentation Requirements:
- Beneficial ownership charts and corporate structure
- Source of funds and wealth documentation
- Business registration and licensing verification
- Risk mitigation measures for identified concerns
"""
    
    def _load_industry_intelligence(self) -> Dict[str, str]:
        return {
            "fintech_financial": """
## 🏦 FINTECH/FINANCIAL SECTOR INTELLIGENCE

### Critical Compliance Areas:
- **Banking Licenses**: Verify required financial services licenses
- **PCI DSS Compliance**: Payment card industry security standards
- **Capital Requirements**: Minimum capital and reserve requirements
- **AML Program**: Anti-money laundering program adequacy
- **GDPR/Privacy**: Customer data protection compliance
- **Regulatory Reporting**: Timely and accurate regulatory submissions

### Key Risk Indicators:
- Unlicensed financial operations
- Inadequate capital reserves
- Poor AML/KYC controls
- Data protection violations
- Regulatory enforcement actions
- High customer complaint ratios

### Enhanced Due Diligence:
- Review banking relationships and correspondent accounts
- Verify customer onboarding procedures
- Assess transaction monitoring systems
- Evaluate cybersecurity frameworks
""",
            "ecommerce_retail": """
## 🛒 E-COMMERCE/RETAIL SECTOR INTELLIGENCE

### Critical Compliance Areas:
- **Consumer Protection**: Return policies, terms of service
- **Payment Security**: PCI compliance for payment processing
- **Product Liability**: Product safety and recall procedures
- **Tax Compliance**: Sales tax collection and remittance
- **Privacy Policies**: Customer data handling practices
- **Advertising Standards**: Truth in advertising compliance

### Key Risk Indicators:
- High chargeback rates
- Customer service complaints
- Product safety violations
- Deceptive advertising practices
- Poor return/refund policies
- Inadequate data security

### Enhanced Due Diligence:
- Verify supplier relationships and product sourcing
- Review customer review authenticity
- Assess inventory management systems
- Evaluate customer service capabilities
""",
            "software_saas": """
## 💻 SOFTWARE/SaaS SECTOR INTELLIGENCE

### Critical Compliance Areas:
- **Data Protection**: GDPR, CCPA compliance implementation
- **Security Certifications**: SOC 2, ISO 27001 certifications
- **Privacy Policies**: Comprehensive data handling disclosure
- **Terms of Service**: Clear service level agreements
- **API Security**: Secure integration and access controls
- **Intellectual Property**: Software licensing and IP protection

### Key Risk Indicators:
- Data breaches or security incidents
- Lack of security certifications
- Poor API security practices
- Unclear data retention policies
- IP infringement issues
- Service availability problems

### Enhanced Due Diligence:
- Review security audit reports
- Verify data center security and compliance
- Assess software development practices
- Evaluate third-party integrations
"""
        }
    
    def build_enhanced_assessment_prompt(self, company_name: str, domain: str, 
                                       industry_category: str, scraped_data: Dict) -> str:
        """Build comprehensive 2025-compliant assessment prompt"""
        
        # Build real-time data context
        real_time_context = self._build_real_time_data_context(scraped_data)
        
        # Get industry-specific intelligence
        industry_intel = self.industry_intelligence.get(
            industry_category, 
            self.industry_intelligence.get("software_saas", "")
        )
        
        # Build enhanced scoring instructions
        scoring_instructions = self._build_enhanced_scoring_instructions()
        
        # Build cross-validation requirements
        cross_validation = self._build_cross_validation_requirements()
        
        # Build JSON structure
        json_structure = self._build_enhanced_json_structure(company_name, domain, industry_category)
        
        # Combine all sections
        complete_prompt = self.base_template.format(
            company_name=company_name,
            domain=domain,
            real_time_data_context=real_time_context,
            compliance_requirements_section=self.compliance_standards,
            industry_specific_intelligence=industry_intel,
            enhanced_scoring_instructions=scoring_instructions,
            cross_validation_requirements=cross_validation,
            json_output_structure=json_structure
        )
        
        return complete_prompt
    
    def _build_real_time_data_context(self, scraped_data: Dict) -> str:
        """Build context section from real-time scraped data"""
        if not scraped_data:
            return "## 📊 REAL-TIME DATA: No scraped data available - conduct assessment based on publicly available information"
        
        context = "## 📊 REAL-TIME SCRAPED DATA ANALYSIS:\n"
        
        # Categorize and format scraped data
        security_data = []
        business_data = []
        compliance_data = []
        
        for source, data in scraped_data.items():
            if source in ["collection_timestamp", "domain", "industry_category"]:
                continue
                
            if isinstance(data, dict) and "error" not in data:
                formatted_item = self._format_scraped_data_item(source, data)
                if formatted_item:
                    if source in ["google_safe_browsing", "ssl_org_report", "ipvoid", "nordvpn_malicious"]:
                        security_data.append(formatted_item)
                    elif source in ["whois_data", "social_presence", "traffic_volume", "tranco_ranking"]:
                        business_data.append(formatted_item)
                    elif source in ["privacy_terms"]:
                        compliance_data.append(formatted_item)
        
        if security_data:
            context += "\n### 🔒 SECURITY INTELLIGENCE:\n" + "\n".join(security_data)
        if business_data:
            context += "\n### 🏢 BUSINESS INTELLIGENCE:\n" + "\n".join(business_data)
        if compliance_data:
            context += "\n### ⚖️ COMPLIANCE DATA:\n" + "\n".join(compliance_data)
        
        context += f"\n\n**Data Collection Timestamp**: {scraped_data.get('collection_timestamp', 'Unknown')}"
        context += f"\n**Sources Collected**: {len([k for k in scraped_data.keys() if not k.startswith('collection_')])}"
        
        return context
    
    def _format_scraped_data_item(self, source: str, data: Dict) -> str:
        """Format individual scraped data items for prompt context"""
        if source == "google_safe_browsing":
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
        elif source == "ipvoid":
            detections = data.get('detections_count', {})
            detected = detections.get('detected', 0) if isinstance(detections, dict) else 0
            return f"- **IP Blacklist Status**: {detected} detections found"
        elif source == "tranco_ranking":
            rank = data.get('Tranco Rank', 'Unknown')
            return f"- **Web Ranking**: Tranco #{rank}"
        elif source == "traffic_volume":
            traffic = data.get('last_month_traffic', 0)
            return f"- **Monthly Traffic**: {traffic} visits"
        else:
            return f"- **{source.replace('_', ' ').title()}**: Data available"
    
    def _build_enhanced_scoring_instructions(self) -> str:
        return """
## 📊 ENHANCED SCORING METHODOLOGY

### Scoring Scale (0-10):
- **8-10**: Excellent - Strong positive indicators, low risk
- **6-7**: Good - Generally positive with minor concerns
- **4-5**: Fair - Mixed indicators, moderate risk
- **2-3**: Poor - Significant concerns, high risk
- **0-1**: Critical - Major red flags, very high risk

### Evidence-Based Scoring:
1. **Primary Evidence**: Use real-time scraped data as primary source
2. **Secondary Evidence**: Use publicly available information for verification
3. **Cross-Validation**: Compare multiple sources for consistency
4. **Confidence Levels**: Assign based on data quality and recency

### Risk Multipliers:
- **High-Risk Industries**: Apply 1.2x multiplier to negative findings
- **High-Risk Jurisdictions**: Apply 1.5x multiplier for sanctioned countries
- **Complex Ownership**: Apply 1.3x multiplier for unclear ownership structures
- **Recent Incorporation**: Apply 1.2x multiplier for companies <2 years old

### Special Considerations:
- **Startup/New Companies**: Use alternative verification methods
- **Private Companies**: Focus on available public information
- **International Companies**: Consider jurisdiction-specific requirements
"""
    
    def _build_cross_validation_requirements(self) -> str:
        return """
## 🔍 CROSS-VALIDATION REQUIREMENTS

### Data Validation Protocol:
1. **Source Reliability**: Prioritize government/regulatory sources
2. **Recency Check**: Flag data older than 12 months
3. **Consistency Check**: Identify conflicts between sources
4. **Completeness Assessment**: Note gaps in available information

### Quality Indicators:
- **High Quality**: 3+ independent sources, recent data, consistent findings
- **Medium Quality**: 2 independent sources, some data gaps
- **Low Quality**: Single source, outdated data, or conflicting information

### Confidence Scoring:
- **High Confidence (0.8-1.0)**: Multiple reliable sources, recent data
- **Medium Confidence (0.5-0.7)**: Limited sources, some uncertainty
- **Low Confidence (0.0-0.4)**: Insufficient data, significant gaps

### Red Flag Protocols:
- **Immediate Escalation**: Sanctions matches, PEP connections
- **Enhanced Review**: Complex ownership, high-risk jurisdictions
- **Standard Review**: Minor inconsistencies, data gaps
"""
    
    def _build_enhanced_json_structure(self, company_name: str, domain: str, industry: str) -> str:
        return f"""
## 📋 REQUIRED JSON OUTPUT STRUCTURE

Return ONLY valid JSON in this exact format:

{{
  "company_name": "{company_name}",
  "domain": "{domain}",
  "assessment_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "assessment_type": "enhanced_2025_compliance",
  "industry_category": "{industry}",
  "compliance_version": "2025.1",
  
  "risk_categories": {{
    "regulatory_compliance_risk": {{
      "checks": [
        {{
          "check_name": "UBO Identification & Verification",
          "score": 0,
          "reason": "Analysis of ultimate beneficial ownership structure",
          "insight": "Key findings about ownership transparency",
          "source": "Corporate registries and ownership data",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
        }},
        {{
          "check_name": "Sanctions & Watchlist Screening",
          "score": 0,
          "reason": "OFAC, EU, UN sanctions screening results",
          "insight": "Sanctions compliance status",
          "source": "Government sanctions databases",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
        }},
        {{
          "check_name": "PEP (Politically Exposed Persons) Screening",
          "score": 0,
          "reason": "Political exposure risk assessment",
          "insight": "Political connections analysis",
          "source": "PEP databases and political records",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": []
        }},
        {{
          "check_name": "Business Registration & Licensing",
          "score": 0,
          "reason": "Corporate registration and licensing verification",
          "insight": "Legal entity status and compliance",
          "source": "Secretary of State and licensing databases",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
        }},
        {{
          "check_name": "Industry-Specific Compliance",
          "score": 0,
          "reason": "Sector-specific regulatory compliance",
          "insight": "Industry regulation adherence",
          "source": "Industry regulators and compliance databases",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": []
        }}
      ],
      "average_score": 0.0,
      "weight": 0.30,
      "category_risk_level": "Medium",
      "compliance_status": "Under Review"
    }},
    
    "financial_transparency_risk": {{
      "checks": [
        {{
          "check_name": "SEC & Regulatory Filings Analysis",
          "score": 0,
          "reason": "Public financial disclosure review",
          "insight": "Financial transparency assessment",
          "source": "SEC EDGAR and regulatory databases",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
        }},
        {{
          "check_name": "Ownership Structure Analysis",
          "score": 0,
          "reason": "Corporate structure complexity assessment",
          "insight": "Ownership transparency evaluation",
          "source": "Corporate filings and ownership records",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": []
        }},
        {{
          "check_name": "Financial Stability Assessment",
          "score": 0,
          "reason": "Financial health and creditworthiness",
          "insight": "Financial stability indicators",
          "source": "Financial reports and credit databases",
          "public_data_available": false,
          "confidence_level": "low",
          "red_flags": []
        }}
      ],
      "average_score": 0.0,
      "weight": 0.25,
      "category_risk_level": "Medium"
    }},
    
    "operational_legitimacy_risk": {{
      "checks": [
        {{
          "check_name": "Business Address & Physical Presence",
          "score": 0,
          "reason": "Physical location and operations verification",
          "insight": "Operational legitimacy assessment",
          "source": "Address verification and business directories",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": []
        }},
        {{
          "check_name": "Employee & Organizational Verification",
          "score": 0,
          "reason": "Workforce and organizational structure",
          "insight": "Operational scale and legitimacy",
          "source": "LinkedIn and employment data",
          "public_data_available": true,
          "confidence_level": "medium",
          "red_flags": []
        }}
      ],
      "average_score": 0.0,
      "weight": 0.20,
      "category_risk_level": "Medium"
    }},
    
    "technology_security_risk": {{
      "checks": [
        {{
          "check_name": "Cybersecurity Posture Assessment",
          "score": 0,
          "reason": "Security controls and certifications",
          "insight": "Cybersecurity maturity level",
          "source": "Security certifications and assessments",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
        }}
      ],
      "average_score": 0.0,
      "weight": 0.15,
      "category_risk_level": "Medium"
    }},
    
    "reputational_intelligence_risk": {{
      "checks": [
        {{
          "check_name": "Adverse Media Screening",
          "score": 0,
          "reason": "Negative news and media analysis",
          "insight": "Public reputation assessment",
          "source": "News databases and media monitoring",
          "public_data_available": true,
          "confidence_level": "high",
          "red_flags": []
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
    "compliance_concerns": [],
    "data_sources_count": 0,
    "assessment_timestamp": "{datetime.now().isoformat()}",
    "compliance_version": "2025.1"
  }},
  
  "recommendations": {{
    "immediate_actions": [],
    "enhanced_monitoring": [],
    "compliance_requirements": [],
    "risk_mitigation": []
  }}
}}
"""

# Utility function to integrate with existing system
def build_enhanced_2025_prompt(company_name: str, domain: str, 
                              industry_category: str, scraped_data: Dict) -> str:
    """Build enhanced 2025-compliant prompt - use this to replace your existing prompt builder"""
    builder = Enhanced2025PromptBuilder()
    return builder.build_enhanced_assessment_prompt(company_name, domain, industry_category, scraped_data)

# Test the enhanced prompt
if __name__ == "__main__":
    test_data = {
        "https_check": {"has_https": True, "protocol": "HTTPS"},
        "google_safe_browsing": {"Current Status": "No unsafe content found"},
        "social_presence": '{"social_presence": {"linkedin": {"presence": true}}, "employee_count": "1000-5000"}'
    }
    
    prompt = build_enhanced_2025_prompt("Shopify", "shopify.com", "ecommerce_retail", test_data)
    print("Enhanced 2025 prompt generated successfully!")
    print(f"Prompt length: {len(prompt)} characters")