# backend/utils/scraper_coordinator.py
# COMPLETE ENHANCED VERSION - Replace your existing scraper_coordinator.py with this

import time
import json
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class EnhancedScraperCoordinator:
    """
    Enhanced scraper coordinator with industry-specific intelligence and 2025 compliance features
    Maintains all your existing functionality + adds new capabilities
    """
    
    def __init__(self, max_workers: int = 3, rate_limit_delay: float = 1.0):
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.results = {}
        self.execution_log = []
        self.industry_config = self._load_industry_configurations()
    
    def _load_industry_configurations(self) -> Dict:
        """Load industry-specific scraper configurations"""
        return {
            "fintech_financial": {
                "priority_scrapers": ["https_check", "whois_data", "privacy_terms", "ssl_org_report", "ofac_sanctions"],
                "compliance_focus": ["sanctions_screening", "financial_licenses", "aml_compliance"],
                "risk_multiplier": 1.3,
                "required_data_sources": 8
            },
            "ecommerce_retail": {
                "priority_scrapers": ["https_check", "privacy_terms", "social_presence", "traffic_volume", "tranco_ranking"],
                "compliance_focus": ["consumer_protection", "payment_security", "privacy_compliance"],
                "risk_multiplier": 1.1,
                "required_data_sources": 6
            },
            "software_saas": {
                "priority_scrapers": ["https_check", "ssl_org_report", "social_presence", "whois_data", "privacy_terms"],
                "compliance_focus": ["data_protection", "security_certifications", "privacy_policies"],
                "risk_multiplier": 1.0,
                "required_data_sources": 7
            },
            "healthcare": {
                "priority_scrapers": ["https_check", "ssl_org_report", "privacy_terms", "whois_data", "ipvoid"],
                "compliance_focus": ["hipaa_compliance", "data_security", "medical_licenses"],
                "risk_multiplier": 1.4,
                "required_data_sources": 9
            },
            "media_social": {
                "priority_scrapers": ["https_check", "social_presence", "traffic_volume", "privacy_terms", "google_safe_browsing"],
                "compliance_focus": ["content_moderation", "privacy_policies", "user_safety"],
                "risk_multiplier": 1.2,
                "required_data_sources": 6
            },
            "default": {
                "priority_scrapers": ["https_check", "whois_data", "privacy_terms", "social_presence"],
                "compliance_focus": ["basic_compliance", "business_verification"],
                "risk_multiplier": 1.0,
                "required_data_sources": 5
            }
        }
    
    def run_scraper_safely(self, scraper_func, *args, **kwargs) -> Dict:
        """Enhanced scraper execution with comprehensive error handling and metadata"""
        scraper_name = scraper_func.__name__
        start_time = time.time()
        
        try:
            print(f"🕷️ Starting {scraper_name}...")
            result = scraper_func(*args, **kwargs)
            
            # Validate and enhance result
            if result is None:
                result = {"error": "Scraper returned None", "scraper": scraper_name}
            elif not isinstance(result, dict):
                result = {"error": f"Invalid result type: {type(result)}", "scraper": scraper_name}
            
            execution_time = round(time.time() - start_time, 2)
            
            # Add enhanced metadata
            result["_scraper_metadata"] = {
                "scraper_name": scraper_name,
                "execution_time_seconds": execution_time,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data_quality": self._assess_data_quality(result),
                "compliance_relevant": self._is_compliance_relevant(scraper_name, result)
            }
            
            print(f"✅ {scraper_name} completed in {execution_time}s")
            return result
            
        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            error_result = {
                "error": str(e),
                "scraper": scraper_name,
                "_scraper_metadata": {
                    "scraper_name": scraper_name,
                    "execution_time_seconds": execution_time,
                    "status": "failed",
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
            }
            print(f"❌ {scraper_name} failed after {execution_time}s: {e}")
            return error_result
    
    def execute_scraper_group(self, scrapers: List[Tuple[str, callable]], 
                            domain: str, group_name: str = "unknown") -> Dict:
        """Execute a group of scrapers in parallel with enhanced coordination"""
        print(f"📊 Executing {group_name} scraper group ({len(scrapers)} scrapers)")
        group_results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scrapers
            future_to_scraper = {
                executor.submit(self.run_scraper_safely, scraper_func, domain): scraper_name
                for scraper_name, scraper_func in scrapers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    result = future.result()
                    group_results[scraper_name] = result
                except Exception as e:
                    group_results[scraper_name] = {
                        "error": f"Future execution failed: {str(e)}",
                        "scraper": scraper_name,
                        "_scraper_metadata": {
                            "scraper_name": scraper_name,
                            "status": "executor_failed",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
        
        # Add rate limiting delay after group execution
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)
        
        print(f"✅ {group_name} group completed: {len(group_results)} results")
        return group_results
    
    def get_industry_scraper_config(self, industry_category: str) -> Dict[str, List]:
        """Get enhanced industry-specific scraper configuration"""
        
        # Import all your existing scrapers
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
            
            # Try to import OFAC scraper if available
            try:
                from scrapers.ofac_sanctions_scraper import check_ofac_sanctions
                OFAC_AVAILABLE = True
                print("✅ OFAC scraper imported in enhanced coordinator")
            except ImportError:
                OFAC_AVAILABLE = False
                print("⚠️ OFAC scraper not available in enhanced coordinator")
                
        except ImportError as e:
            print(f"⚠️ Some scrapers not available: {e}")
            return {"critical": [], "high": [], "medium": [], "enhanced": []}
        
        # Get industry-specific configuration
        industry_config = self.industry_config.get(industry_category, self.industry_config["default"])
        
        # Base configuration that works with your existing scrapers
        base_config = {
            "critical": [
                ("https_check", check_https),
                ("privacy_terms", check_privacy_term),
                ("whois_data", get_whois_data),
            ],
            "high": [
                ("google_safe_browsing", scrape_google_safe_browsing),
                ("ssl_org_report", scrape_ssl_org),
                ("social_presence", check_social_presence),
                ("tranco_ranking", scrape_tranco_list)
            ],
            "medium": [
                ("ipvoid", scrape_ipvoid),
            ],
            "enhanced": []  # For new enhanced scrapers
        }
        
        # Add OFAC to critical scrapers if available
        if OFAC_AVAILABLE:
            # Create a wrapper that extracts company name from domain for OFAC
            def ofac_domain_wrapper(domain):
                company_name = domain.split('.')[0].capitalize()
                return check_ofac_sanctions(company_name, domain)
            
            base_config["critical"].append(("ofac_sanctions", ofac_domain_wrapper))
            print("✅ OFAC sanctions scraper added to critical scrapers")
        
        # Industry-specific enhancements
        if industry_category == "fintech_financial":
            # FinTech: Focus on compliance and security
            print(f"🏦 Applying FinTech-specific scraper configuration")
            base_config["high"].insert(0, ("ssl_org_report", scrape_ssl_org))  # Prioritize security
            
        elif industry_category == "ecommerce_retail":
            # E-commerce: Focus on customer trust and performance
            print(f"🛒 Applying E-commerce-specific scraper configuration")
            base_config["high"].insert(0, ("tranco_ranking", scrape_tranco_list))  # Prioritize traffic analysis
            
        elif industry_category == "software_saas":
            # SaaS: Focus on technical infrastructure and data protection
            print(f"💻 Applying SaaS-specific scraper configuration")
            base_config["critical"].insert(1, ("ssl_org_report", scrape_ssl_org))  # Security is critical
            
        elif industry_category == "healthcare":
            # Healthcare: Maximum security and compliance focus
            print(f"🏥 Applying Healthcare-specific scraper configuration")
            base_config["critical"].extend([
                ("ssl_org_report", scrape_ssl_org),
                ("ipvoid", scrape_ipvoid)
            ])
            
        elif industry_category == "media_social":
            # Media/Social: Focus on content and public presence
            print(f"📱 Applying Media/Social-specific scraper configuration")
            base_config["high"].insert(0, ("social_presence", check_social_presence))  # Prioritize social analysis
        
        return base_config
    
    def coordinate_full_assessment(self, domain: str, industry_category: str = "software_saas") -> Dict:
        """Enhanced coordination with industry-specific intelligence"""
        print(f"🚀 Starting enhanced coordinated assessment for {domain}")
        print(f"🎯 Industry Category: {industry_category}")
        start_time = time.time()
        
        # Get industry-specific configuration
        industry_config = self.industry_config.get(industry_category, self.industry_config["default"])
        scraper_config = self.get_industry_scraper_config(industry_category)
        
        all_results = {
            "coordination_metadata": {
                "domain": domain,
                "industry_category": industry_category,
                "industry_config": industry_config,
                "start_time": datetime.now().isoformat(),
                "coordinator_version": "enhanced_v2.0_industry_specific",
                "ofac_screening_enabled": True,
                "compliance_focus": industry_config.get("compliance_focus", []),
                "risk_multiplier": industry_config.get("risk_multiplier", 1.0)
            }
        }
        
        # Execute scraper groups in priority order with industry focus
        execution_order = ["critical", "high", "medium", "enhanced"]
        
        for priority_level in execution_order:
            if priority_level in scraper_config and scraper_config[priority_level]:
                group_results = self.execute_scraper_group(
                    scraper_config[priority_level], 
                    domain, 
                    f"{priority_level}_priority_{industry_category}"
                )
                all_results.update(group_results)
        
        # Industry classification if not already done
        if "industry_classification" not in all_results:
            all_results["industry_classification"] = self._classify_industry(domain, all_results)
        
        # Handle IP-based scrapers
        ip_address = self._extract_ip_from_results(all_results)
        if ip_address:
            print(f"🌐 Running IP-based scrapers for: {ip_address}")
            ip_results = self._run_ip_based_scrapers(ip_address)
            all_results.update(ip_results)
        
        # Enhanced final metadata with industry insights
        total_time = round(time.time() - start_time, 2)
        all_results["coordination_metadata"].update({
            "total_execution_time_seconds": total_time,
            "completion_time": datetime.now().isoformat(),
            "scrapers_executed": len([k for k in all_results.keys() if not k.startswith("coordination_")]),
            "successful_scrapers": len([k for k, v in all_results.items() 
                                      if isinstance(v, dict) and "error" not in v]),
            "failed_scrapers": len([k for k, v in all_results.items() 
                                  if isinstance(v, dict) and "error" in v]),
            "ofac_screening_completed": "ofac_sanctions" in all_results,
            "industry_requirements_met": self._check_industry_requirements(all_results, industry_config),
            "data_quality_score": self._calculate_overall_data_quality(all_results),
            "compliance_score": self._calculate_compliance_score(all_results, industry_category)
        })
        
        print(f"✅ Enhanced coordinated assessment completed in {total_time}s")
        return all_results
    
    def _classify_industry(self, domain: str, results: Dict) -> Dict:
        """Enhanced industry classification using available data"""
        try:
            from scrapers.mcc_classifier_gemini_final import classify_mcc_using_gemini, extract_text_from_url
            
            website_url = f"https://{domain}"
            website_content = extract_text_from_url(website_url)
            
            if website_content and not website_content.startswith("Failed"):
                classification = classify_mcc_using_gemini(domain, website_content[:1000])
                
                # Enhance classification with scraped data insights
                if isinstance(classification, dict):
                    classification["enhanced_classification"] = self._enhance_industry_classification(
                        classification, results
                    )
                
                return classification
            else:
                return {
                    "industry_category": "unknown", 
                    "confidence": 0.3,
                    "classification_method": "fallback"
                }
                
        except Exception as e:
            print(f"⚠️ Industry classification failed: {e}")
            return {
                "industry_category": "unknown",
                "error": str(e),
                "classification_method": "failed"
            }
    
    def _enhance_industry_classification(self, base_classification: Dict, results: Dict) -> Dict:
        """Enhance industry classification using scraped data"""
        enhancements = {
            "data_sources_analyzed": len(results),
            "confidence_boosters": [],
            "industry_indicators": []
        }
        
        # Analyze scraped data for industry indicators
        if "social_presence" in results:
            social_data = results["social_presence"]
            if isinstance(social_data, dict) and not social_data.get("error"):
                try:
                    if isinstance(social_data, str):
                        social_parsed = json.loads(social_data)
                    else:
                        social_parsed = social_data
                    
                    employee_count = social_parsed.get("employee_count", "unknown")
                    if employee_count != "unknown":
                        enhancements["confidence_boosters"].append("employee_data_available")
                        enhancements["industry_indicators"].append(f"employee_scale_{employee_count}")
                except:
                    pass
        
        # Check for FinTech indicators
        if "privacy_terms" in results:
            privacy_data = results["privacy_terms"]
            if isinstance(privacy_data, dict) and privacy_data.get("privacy_policy_present"):
                enhancements["confidence_boosters"].append("privacy_policy_present")
        
        # Check for security indicators
        if "ssl_org_report" in results:
            ssl_data = results["ssl_org_report"]
            if isinstance(ssl_data, dict) and not ssl_data.get("error"):
                ssl_grade = ssl_data.get("report_summary", {}).get("ssl_grade", "")
                if ssl_grade in ["A+", "A", "A-"]:
                    enhancements["confidence_boosters"].append("high_security_grade")
                    enhancements["industry_indicators"].append("security_focused")
        
        return enhancements
    
    def _assess_data_quality(self, result: Dict) -> str:
        """Assess the quality of data returned by a scraper"""
        if result.get("error"):
            return "poor"
        
        # Count meaningful data fields (excluding metadata)
        meaningful_fields = [k for k in result.keys() if not k.startswith("_") and k != "error"]
        
        if len(meaningful_fields) >= 5:
            return "high"
        elif len(meaningful_fields) >= 3:
            return "medium"
        else:
            return "low"
    
    def _is_compliance_relevant(self, scraper_name: str, result: Dict) -> bool:
        """Determine if scraper result is relevant for compliance"""
        compliance_relevant_scrapers = [
            "ofac_sanctions", "privacy_terms", "ssl_org_report", 
            "google_safe_browsing", "whois_data", "ipvoid"
        ]
        return scraper_name in compliance_relevant_scrapers and not result.get("error")
    
    def _check_industry_requirements(self, results: Dict, industry_config: Dict) -> bool:
        """Check if industry-specific requirements are met"""
        required_sources = industry_config.get("required_data_sources", 5)
        successful_scrapers = len([k for k, v in results.items() 
                                 if isinstance(v, dict) and not v.get("error") 
                                 and not k.startswith("coordination_")])
        
        return successful_scrapers >= required_sources
    
    def _calculate_overall_data_quality(self, results: Dict) -> float:
        """Calculate overall data quality score"""
        quality_scores = []
        
        for key, result in results.items():
            if key.startswith("coordination_") or not isinstance(result, dict):
                continue
                
            metadata = result.get("_scraper_metadata", {})
            quality = metadata.get("data_quality", "medium")
            
            score_map = {"high": 1.0, "medium": 0.6, "low": 0.3, "poor": 0.0}
            quality_scores.append(score_map.get(quality, 0.0))
        
        return round(sum(quality_scores) / max(len(quality_scores), 1), 2)
    
    def _calculate_compliance_score(self, results: Dict, industry_category: str) -> float:
        """Calculate compliance score based on industry requirements"""
        industry_config = self.industry_config.get(industry_category, self.industry_config["default"])
        compliance_focus = industry_config.get("compliance_focus", [])
        
        compliance_score = 0.0
        max_score = len(compliance_focus) if compliance_focus else 1
        
        # Check specific compliance areas
        if "sanctions_screening" in compliance_focus and "ofac_sanctions" in results:
            ofac_result = results["ofac_sanctions"]
            if not ofac_result.get("error"):
                compliance_score += 1.0
        
        if "data_protection" in compliance_focus and "privacy_terms" in results:
            privacy_result = results["privacy_terms"]
            if privacy_result.get("privacy_policy_present"):
                compliance_score += 1.0
        
        if "security_certifications" in compliance_focus and "ssl_org_report" in results:
            ssl_result = results["ssl_org_report"]
            ssl_grade = ssl_result.get("report_summary", {}).get("ssl_grade", "")
            if ssl_grade in ["A+", "A", "A-"]:
                compliance_score += 1.0
        
        return round(compliance_score / max_score, 2)
    
    def _extract_ip_from_results(self, results: Dict) -> Optional[str]:
        """Extract IP address from scraper results for IP-based scrapers"""
        for key, data in results.items():
            if isinstance(data, dict):
                for ip_field in ["ip_address", "IP", "server_ip", "resolved_ip"]:
                    if ip_field in data:
                        return data[ip_field]
        return None
    
    def _run_ip_based_scrapers(self, ip_address: str) -> Dict:
        """Run scrapers that require IP address"""
        try:
            from scrapers.ipvoid_scraper import scrape_ipvoid
            
            ip_results = {}
            ip_results["ipvoid_ip"] = self.run_scraper_safely(scrape_ipvoid, ip_address)
            
            return ip_results
        except ImportError:
            print("⚠️ IP-based scrapers not available")
            return {}
    
    def generate_enhanced_assessment_summary(self, results: Dict) -> Dict:
        """Generate enhanced assessment summary with industry insights"""
        summary = {
            "assessment_summary": {
                "total_scrapers": 0,
                "successful_scrapers": 0,
                "failed_scrapers": 0,
                "data_quality_score": 0.0,
                "compliance_score": 0.0,
                "industry_category": "unknown",
                "key_findings": [],
                "risk_indicators": [],
                "compliance_status": {
                    "ofac_screening_completed": False,
                    "ofac_status": "UNKNOWN",
                    "sanctions_risk": "UNKNOWN",
                    "industry_compliance": "UNKNOWN"
                },
                "industry_insights": {
                    "requirements_met": False,
                    "risk_multiplier": 1.0,
                    "compliance_focus": []
                }
            }
        }
        
        successful = 0
        total = 0
        key_findings = []
        risk_indicators = []
        
        # Get industry information
        industry_category = results.get("coordination_metadata", {}).get("industry_category", "unknown")
        industry_config = self.industry_config.get(industry_category, self.industry_config["default"])
        
        # Check for OFAC screening results
        ofac_results = results.get("ofac_sanctions", {})
        if ofac_results and "error" not in ofac_results:
            summary["assessment_summary"]["compliance_status"] = {
                "ofac_screening_completed": True,
                "ofac_status": ofac_results.get("sanctions_screening", {}).get("status", "UNKNOWN"),
                "sanctions_risk": ofac_results.get("sanctions_screening", {}).get("risk_level", "UNKNOWN"),
                "ofac_compliant": ofac_results.get("compliance_assessment", {}).get("ofac_compliant", False)
            }
            
            # Add OFAC findings
            if ofac_results.get("sanctions_screening", {}).get("total_matches", 0) > 0:
                risk_indicators.append("OFAC sanctions matches found - immediate escalation required")
            else:
                key_findings.append("OFAC sanctions screening clear")
        
        # Analyze all scraper results
        for key, data in results.items():
            if key.startswith("coordination_") or key.startswith("assessment_"):
                continue
                
            total += 1
            if isinstance(data, dict):
                if "error" not in data:
                    successful += 1
                    # Extract key findings
                    findings = self._extract_enhanced_key_findings(key, data, industry_category)
                    key_findings.extend(findings)
                    
                    # Check for risk indicators
                    risks = self._check_enhanced_risk_indicators(key, data, industry_category)
                    risk_indicators.extend(risks)
        
        # Update summary with calculated values
        summary["assessment_summary"].update({
            "total_scrapers": total,
            "successful_scrapers": successful,
            "failed_scrapers": total - successful,
            "data_quality_score": self._calculate_overall_data_quality(results),
            "compliance_score": self._calculate_compliance_score(results, industry_category),
            "industry_category": industry_category,
            "key_findings": key_findings[:10],  # Limit to top 10
            "risk_indicators": risk_indicators[:5],  # Limit to top 5 risks
            "industry_insights": {
                "requirements_met": self._check_industry_requirements(results, industry_config),
                "risk_multiplier": industry_config.get("risk_multiplier", 1.0),
                "compliance_focus": industry_config.get("compliance_focus", [])
            }
        })
        
        return summary
    
    def _extract_enhanced_key_findings(self, scraper_name: str, data: Dict, industry_category: str) -> List[str]:
        """Extract enhanced key findings with industry context"""
        findings = []
        
        if scraper_name == "https_check":
            if data.get("has_https"):
                findings.append("✅ HTTPS encryption implemented (industry requirement)")
            else:
                findings.append("⚠️ Missing HTTPS encryption (critical for " + industry_category + ")")
                
        elif scraper_name == "social_presence":
            if isinstance(data, str):
                try:
                    social_data = json.loads(data)
                except:
                    social_data = {}
            else:
                social_data = data
                
            linkedin = social_data.get("social_presence", {}).get("linkedin", {})
            if linkedin.get("presence"):
                employee_count = social_data.get("employee_count", "unknown")
                findings.append(f"✅ Professional LinkedIn presence with {employee_count} employees")
                
        elif scraper_name == "privacy_terms":
            privacy_present = data.get("privacy_policy_present", False)
            terms_present = data.get("terms_of_service_present", False)
            
            if privacy_present and terms_present:
                findings.append(f"✅ Complete legal documentation (critical for {industry_category})")
            elif privacy_present:
                findings.append("⚠️ Privacy policy present but missing terms of service")
            else:
                findings.append(f"❌ Missing privacy policy (regulatory requirement for {industry_category})")
                
        elif scraper_name == "ssl_org_report":
            ssl_grade = data.get("report_summary", {}).get("ssl_grade", "")
            if ssl_grade in ["A+", "A"]:
                findings.append(f"✅ Excellent SSL security grade: {ssl_grade}")
            elif ssl_grade in ["A-", "B"]:
                findings.append(f"⚠️ Good SSL security grade: {ssl_grade}")
            elif ssl_grade:
                findings.append(f"❌ Poor SSL security grade: {ssl_grade}")
                
        elif scraper_name == "ofac_sanctions":
            sanctions_screening = data.get("sanctions_screening", {})
            status = sanctions_screening.get("status", "UNKNOWN")
            total_matches = sanctions_screening.get("total_matches", 0)
            
            if status == "CLEAR" and total_matches == 0:
                findings.append("✅ OFAC sanctions screening clear - full compliance")
            elif total_matches > 0:
                findings.append(f"🚨 OFAC screening: {total_matches} potential matches require immediate review")
        
        return findings
    
    def _check_enhanced_risk_indicators(self, scraper_name: str, data: Dict, industry_category: str) -> List[str]:
        """Check for enhanced risk indicators with industry context"""
        risks = []
        
        # Industry-specific risk multipliers
        industry_config = self.industry_config.get(industry_category, self.industry_config["default"])
        risk_multiplier = industry_config.get("risk_multiplier", 1.0)
        
        if scraper_name == "https_check" and not data.get("has_https"):
            if industry_category in ["fintech_financial", "healthcare"]:
                risks.append("🚨 CRITICAL: No HTTPS encryption in regulated industry")
            else:
                risks.append("⚠️ No HTTPS encryption - security risk")
                
        elif scraper_name == "google_safe_browsing":
            status = data.get("Current Status", "").lower()
            if "unsafe" in status or "malicious" in status:
                risks.append("🚨 CRITICAL: Flagged as unsafe by Google Safe Browsing")
                
        elif scraper_name == "privacy_terms":
            if not data.get("privacy_policy_present"):
                if industry_category in ["fintech_financial", "healthcare", "ecommerce_retail"]:
                    risks.append("🚨 REGULATORY RISK: No privacy policy in regulated industry")
                else:
                    risks.append("⚠️ No privacy policy found")
                    
        elif scraper_name == "ofac_sanctions":
            sanctions_screening = data.get("sanctions_screening", {})
            risk_level = sanctions_screening.get("risk_level", "CLEAR")
            total_matches = sanctions_screening.get("total_matches", 0)
            
            if risk_level == "HIGH_RISK":
                risks.append("🚨 CRITICAL: HIGH RISK OFAC sanctions matches - immediate escalation required")
            elif risk_level == "MEDIUM_RISK":
                risks.append("⚠️ MEDIUM RISK: OFAC potential matches - enhanced due diligence required")
            elif total_matches > 0:
                risks.append(f"⚠️ OFAC screening flagged {total_matches} potential matches for review")
        
        # Apply industry risk multiplier conceptually
        if risks and risk_multiplier > 1.2:
            risks = [f"[HIGH RISK INDUSTRY] {risk}" for risk in risks]
        
        return risks

# Utility functions for easy import and backward compatibility
def coordinate_scrapers(domain: str, industry_category: str = "software_saas", 
                       max_workers: int = 3, rate_limit_delay: float = 1.0) -> Dict:
    """Enhanced convenience function to coordinate scrapers with industry intelligence"""
    coordinator = EnhancedScraperCoordinator(max_workers=max_workers, rate_limit_delay=rate_limit_delay)
    results = coordinator.coordinate_full_assessment(domain, industry_category)
    summary = coordinator.generate_enhanced_assessment_summary(results)
    results.update(summary)
    return results

def quick_scraper_test(domain: str, industry_category: str = "software_saas") -> Dict:
    """Quick test with basic scrapers including enhanced features"""
    coordinator = EnhancedScraperCoordinator(max_workers=2, rate_limit_delay=0.5)
    
    try:
        from scrapers.check_https import check_https
        from scrapers.check_privacy_term import check_privacy_term
        
        basic_scrapers = [
            ("https_check", check_https),
            ("privacy_terms", check_privacy_term)
        ]
        
        # Add OFAC if available
        try:
            from scrapers.ofac_sanctions_scraper import check_ofac_sanctions
            
            def ofac_test_wrapper(domain):
                company_name = domain.split('.')[0].capitalize()
                return check_ofac_sanctions(company_name, domain)
            
            basic_scrapers.append(("ofac_sanctions", ofac_test_wrapper))
            print("✅ OFAC added to quick test")
        except ImportError:
            print("⚠️ OFAC not available for quick test")
        
        results = coordinator.execute_scraper_group(basic_scrapers, domain, f"quick_test_{industry_category}")
        
        # Add industry classification
        results["industry_classification"] = coordinator._classify_industry(domain, results)
        
        return results
        
    except ImportError as e:
        return {"error": f"Basic scrapers not available: {e}"}

# Test the enhanced coordinator
if __name__ == "__main__":
    test_domain = "shopify.com"
    industry = "ecommerce_retail"
    
    print(f"Testing enhanced scraper coordinator for: {test_domain} (Industry: {industry})")
    
    # Quick test
    print("\n=== ENHANCED QUICK TEST ===")
    quick_results = quick_scraper_test(test_domain, industry)
    print("Enhanced quick test results:")
    print(json.dumps(quick_results, indent=2))
    
    # Full coordination test (uncomment to test)
    # print("\n=== FULL ENHANCED COORDINATION TEST ===")
    # full_results = coordinate_scrapers(test_domain, industry)
    # print("Full enhanced coordination results:")
    # print(json.dumps(full_results, indent=2))