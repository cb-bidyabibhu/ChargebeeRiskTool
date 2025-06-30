# backend/utils/scraper_coordinator.py
# COMPLETE FILE - Copy this entire content to: backend/utils/scraper_coordinator.py

import time
import json
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class ScraperCoordinator:
    """
    Coordinates execution of multiple scrapers with rate limiting, error handling,
    and industry-specific prioritization including OFAC sanctions screening
    """
    
    def __init__(self, max_workers: int = 3, rate_limit_delay: float = 1.0):
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.results = {}
        self.execution_log = []
    
    def run_scraper_safely(self, scraper_func, *args, **kwargs) -> Dict:
        """Run a single scraper with comprehensive error handling"""
        scraper_name = scraper_func.__name__
        start_time = time.time()
        
        try:
            print(f"🕷️ Starting {scraper_name}...")
            result = scraper_func(*args, **kwargs)
            
            # Validate result
            if result is None:
                result = {"error": "Scraper returned None", "scraper": scraper_name}
            elif not isinstance(result, dict):
                result = {"error": f"Invalid result type: {type(result)}", "scraper": scraper_name}
            
            execution_time = round(time.time() - start_time, 2)
            result["_scraper_metadata"] = {
                "scraper_name": scraper_name,
                "execution_time_seconds": execution_time,
                "status": "success",
                "timestamp": datetime.now().isoformat()
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
                    "timestamp": datetime.now().isoformat()
                }
            }
            print(f"❌ {scraper_name} failed after {execution_time}s: {e}")
            return error_result
    
    def execute_scraper_group(self, scrapers: List[Tuple[str, callable]], 
                            domain: str, group_name: str = "unknown") -> Dict:
        """Execute a group of scrapers in parallel"""
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
                        "scraper": scraper_name
                    }
        
        # Add rate limiting delay after group execution
        if self.rate_limit_delay > 0:
            time.sleep(self.rate_limit_delay)
        
        print(f"✅ {group_name} group completed: {len(group_results)} results")
        return group_results
    
    def get_industry_scraper_config(self, industry_category: str) -> Dict[str, List]:
        """Get industry-specific scraper configuration with OFAC screening"""
        
        # Import scrapers here to avoid circular imports
        try:
            from scrapers.check_https import check_https
            from scrapers.whois_sraper import get_whois_data
            from scrapers.get_ssl_fingerprint import get_ssl_fingerprint
            from scrapers.check_privacy_term import check_privacy_term
            from scrapers.godaddy_whois_scraper import scrape_godaddy_whois
            from scrapers.ssl_org_scraper import scrape_ssl_org
            from scrapers.ssltrust_blacklist_scraper import scrape_ssltrust_blacklist
            from scrapers.google_safe_browsing_scraper import scrape_google_safe_browsing
            from scrapers.tranco_list_scraper import scrape_tranco_list
            from scrapers.traffic_vol import check_traffic
            from scrapers.mxtool_scraper import scrape_mxtoolbox
            from scrapers.pagesize_scraper import scrape_page_size
            from scrapers.check_linkedin import check_social_presence
            from scrapers.check_malicious_nordvpn import check_malicious_nordvpn
            
            # Import OFAC scraper
            from scrapers.ofac_sanctions_scraper import check_ofac_sanctions
            OFAC_AVAILABLE = True
            print("✅ OFAC scraper imported in coordinator")
            
        except ImportError as e:
            print(f"⚠️ Some scrapers not available: {e}")
            OFAC_AVAILABLE = False
            return {"critical": [], "high": [], "medium": []}
        
        # Base configuration for all industries with OFAC included
        base_config = {
            "critical": [
                ("https_check", check_https),
                ("privacy_terms", check_privacy_term),
                ("whois_data", get_whois_data),
                ("ssl_fingerprint", get_ssl_fingerprint)
            ],
            "high": [
                ("google_safe_browsing", scrape_google_safe_browsing),
                ("ssl_org_report", scrape_ssl_org),
                ("social_presence", check_social_presence),
                ("tranco_ranking", scrape_tranco_list)
            ],
            "medium": [
                ("ssltrust_blacklist", scrape_ssltrust_blacklist),
                ("nordvpn_malicious", check_malicious_nordvpn),
                ("traffic_volume", check_traffic),
                ("godaddy_whois", scrape_godaddy_whois)
            ]
        }
        
        # Add OFAC to critical scrapers if available
        if OFAC_AVAILABLE:
            # Create a lambda that extracts company name from domain for OFAC
            def ofac_domain_wrapper(domain):
                # Extract company name from domain for OFAC screening
                company_name = domain.split('.')[0].capitalize()
                return check_ofac_sanctions(company_name, domain)
            
            base_config["critical"].append(("ofac_sanctions", ofac_domain_wrapper))
            print("✅ OFAC sanctions scraper added to critical scrapers")
        
        # Industry-specific enhancements
        if industry_category == "software_saas":
            # SaaS companies - focus on technical infrastructure and security
            base_config["high"].extend([
                ("mxtoolbox", scrape_mxtoolbox),
                ("page_metrics", scrape_page_size)
            ])
            
        elif industry_category == "ecommerce_retail":
            # E-commerce - focus on customer trust and performance
            base_config["high"].extend([
                ("page_metrics", scrape_page_size)
            ])
            
        elif industry_category == "fintech_financial":
            # FinTech - focus on security and compliance
            base_config["critical"].extend([
                ("mxtoolbox", scrape_mxtoolbox)
            ])
            
        elif industry_category == "media_social":
            # Media/Social - focus on content and social presence
            base_config["high"].extend([
                ("page_metrics", scrape_page_size)
            ])
        
        return base_config
    
    def coordinate_full_assessment(self, domain: str, industry_category: str = "other") -> Dict:
        """Coordinate a full assessment with all relevant scrapers including OFAC"""
        print(f"🚀 Starting coordinated assessment for {domain} (Industry: {industry_category})")
        start_time = time.time()
        
        # Get industry-specific scraper configuration
        scraper_config = self.get_industry_scraper_config(industry_category)
        
        all_results = {
            "coordination_metadata": {
                "domain": domain,
                "industry_category": industry_category,
                "start_time": datetime.now().isoformat(),
                "coordinator_version": "v2.0_with_ofac",
                "ofac_screening_enabled": True
            }
        }
        
        # Execute scraper groups in priority order
        for priority_level in ["critical", "high", "medium"]:
            if priority_level in scraper_config and scraper_config[priority_level]:
                group_results = self.execute_scraper_group(
                    scraper_config[priority_level], 
                    domain, 
                    f"{priority_level}_priority"
                )
                all_results.update(group_results)
        
        # Handle IP-based scrapers
        ip_address = self._extract_ip_from_results(all_results)
        if ip_address:
            print(f"🌐 Running IP-based scrapers for: {ip_address}")
            ip_results = self._run_ip_based_scrapers(ip_address)
            all_results.update(ip_results)
        
        # Add final metadata
        total_time = round(time.time() - start_time, 2)
        all_results["coordination_metadata"].update({
            "total_execution_time_seconds": total_time,
            "completion_time": datetime.now().isoformat(),
            "scrapers_executed": len([k for k in all_results.keys() if not k.startswith("coordination_")]),
            "successful_scrapers": len([k for k, v in all_results.items() 
                                      if isinstance(v, dict) and "error" not in v]),
            "failed_scrapers": len([k for k, v in all_results.items() 
                                  if isinstance(v, dict) and "error" in v]),
            "ofac_screening_completed": "ofac_sanctions" in all_results
        })
        
        print(f"✅ Coordinated assessment completed in {total_time}s")
        return all_results
    
    def _extract_ip_from_results(self, results: Dict) -> Optional[str]:
        """Extract IP address from scraper results for IP-based scrapers"""
        for key, data in results.items():
            if isinstance(data, dict):
                # Look for IP in various possible fields
                for ip_field in ["ip_address", "IP", "server_ip", "resolved_ip"]:
                    if ip_field in data:
                        return data[ip_field]
        return None
    
    def _run_ip_based_scrapers(self, ip_address: str) -> Dict:
        """Run scrapers that require IP address"""
        try:
            from scrapers.ipvoid_scraper import scrape_ipvoid
            
            ip_results = {}
            ip_results["ipvoid"] = self.run_scraper_safely(scrape_ipvoid, ip_address)
            
            return ip_results
        except ImportError:
            print("⚠️ IP-based scrapers not available")
            return {}
    
    def generate_assessment_summary(self, results: Dict) -> Dict:
        """Generate a summary of the scraping assessment with OFAC status"""
        summary = {
            "assessment_summary": {
                "total_scrapers": 0,
                "successful_scrapers": 0,
                "failed_scrapers": 0,
                "data_quality_score": 0.0,
                "key_findings": [],
                "risk_indicators": [],
                "compliance_status": {
                    "ofac_screening_completed": False,
                    "ofac_status": "UNKNOWN",
                    "sanctions_risk": "UNKNOWN"
                }
            }
        }
        
        successful = 0
        total = 0
        key_findings = []
        risk_indicators = []
        
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
                risk_indicators.append("OFAC sanctions matches found - requires immediate review")
            else:
                key_findings.append("OFAC sanctions screening clear")
        
        for key, data in results.items():
            if key.startswith("coordination_") or key.startswith("assessment_"):
                continue
                
            total += 1
            if isinstance(data, dict):
                if "error" not in data:
                    successful += 1
                    # Extract key findings
                    findings = self._extract_key_findings(key, data)
                    key_findings.extend(findings)
                    
                    # Check for risk indicators
                    risks = self._check_risk_indicators(key, data)
                    risk_indicators.extend(risks)
        
        summary["assessment_summary"].update({
            "total_scrapers": total,
            "successful_scrapers": successful,
            "failed_scrapers": total - successful,
            "data_quality_score": round(successful / total, 2) if total > 0 else 0.0,
            "key_findings": key_findings[:10],  # Limit to top 10
            "risk_indicators": risk_indicators[:5]  # Limit to top 5 risks
        })
        
        return summary
    
    def _extract_key_findings(self, scraper_name: str, data: Dict) -> List[str]:
        """Extract key findings from scraper results including OFAC"""
        findings = []
        
        if scraper_name == "https_check":
            if data.get("has_https"):
                findings.append("Website supports HTTPS encryption")
            else:
                findings.append("Website lacks HTTPS encryption")
                
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
                findings.append(f"Active LinkedIn presence with {employee_count} employees")
                
        elif scraper_name == "google_safe_browsing":
            status = data.get("Current Status", "").lower()
            if "safe" in status or "no" in status:
                findings.append("Clean Google Safe Browsing status")
            elif "unsafe" in status or "malicious" in status:
                findings.append("Flagged by Google Safe Browsing")
                
        elif scraper_name == "tranco_ranking":
            rank = data.get("Tranco Rank", "")
            if rank and rank != "unknown" and rank.isdigit():
                findings.append(f"Tranco ranking: #{rank}")
                
        elif scraper_name == "ofac_sanctions":
            sanctions_screening = data.get("sanctions_screening", {})
            status = sanctions_screening.get("status", "UNKNOWN")
            total_matches = sanctions_screening.get("total_matches", 0)
            
            if status == "CLEAR" and total_matches == 0:
                findings.append("OFAC sanctions screening clear - no matches found")
            elif total_matches > 0:
                findings.append(f"OFAC screening: {total_matches} potential matches require review")
        
        return findings
    
    def _check_risk_indicators(self, scraper_name: str, data: Dict) -> List[str]:
        """Check for risk indicators in scraper results including OFAC"""
        risks = []
        
        if scraper_name == "https_check" and not data.get("has_https"):
            risks.append("No HTTPS encryption - security risk")
            
        elif scraper_name == "google_safe_browsing":
            status = data.get("Current Status", "").lower()
            if "unsafe" in status or "malicious" in status:
                risks.append("Flagged as unsafe by Google")
                
        elif scraper_name == "nordvpn_malicious":
            if data.get("is_malicious_nordvpn"):
                risks.append("Flagged as malicious by NordVPN")
                
        elif scraper_name == "privacy_terms":
            if not data.get("privacy_policy_present"):
                risks.append("No privacy policy found")
            if not data.get("terms_of_service_present"):
                risks.append("No terms of service found")
                
        elif scraper_name == "ipvoid":
            detections = data.get("detections_count", {})
            if isinstance(detections, dict) and detections.get("detected", 0) > 0:
                risks.append(f"IP blacklisted by {detections['detected']} sources")
                
        elif scraper_name == "ofac_sanctions":
            sanctions_screening = data.get("sanctions_screening", {})
            risk_level = sanctions_screening.get("risk_level", "CLEAR")
            total_matches = sanctions_screening.get("total_matches", 0)
            
            if risk_level == "HIGH_RISK":
                risks.append("HIGH RISK: OFAC sanctions matches - immediate escalation required")
            elif risk_level == "MEDIUM_RISK":
                risks.append("MEDIUM RISK: OFAC potential matches - enhanced due diligence required")
            elif total_matches > 0:
                risks.append(f"OFAC screening flagged {total_matches} potential matches")
        
        return risks

# Utility functions for easy import
def coordinate_scrapers(domain: str, industry_category: str = "other", 
                       max_workers: int = 3, rate_limit_delay: float = 1.0) -> Dict:
    """Convenience function to coordinate scrapers for a domain with OFAC screening"""
    coordinator = ScraperCoordinator(max_workers=max_workers, rate_limit_delay=rate_limit_delay)
    results = coordinator.coordinate_full_assessment(domain, industry_category)
    summary = coordinator.generate_assessment_summary(results)
    results.update(summary)
    return results

def quick_scraper_test(domain: str) -> Dict:
    """Quick test with basic scrapers including OFAC if available"""
    coordinator = ScraperCoordinator(max_workers=2, rate_limit_delay=0.5)
    
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
        
        results = coordinator.execute_scraper_group(basic_scrapers, domain, "quick_test")
        return results
        
    except ImportError as e:
        return {"error": f"Basic scrapers not available: {e}"}

def test_ofac_only(domain: str) -> Dict:
    """Test OFAC scraper only"""
    try:
        from scrapers.ofac_sanctions_scraper import check_ofac_sanctions
        
        company_name = domain.split('.')[0].capitalize()
        print(f"🔍 Testing OFAC screening for {company_name} ({domain})")
        
        result = check_ofac_sanctions(company_name, domain)
        return {"ofac_test_result": result}
        
    except ImportError:
        return {"error": "OFAC scraper not available"}
    except Exception as e:
        return {"error": f"OFAC test failed: {str(e)}"}

# Test the coordinator
if __name__ == "__main__":
    test_domain = "shopify.com"
    print(f"Testing scraper coordinator with OFAC for: {test_domain}")
    
    # Quick test with OFAC
    print("\n=== QUICK TEST WITH OFAC ===")
    quick_results = quick_scraper_test(test_domain)
    print("Quick test results:")
    print(json.dumps(quick_results, indent=2))
    
    # OFAC only test
    print("\n=== OFAC ONLY TEST ===")
    ofac_results = test_ofac_only(test_domain)
    print("OFAC test results:")
    print(json.dumps(ofac_results, indent=2))
    
    # Full coordination test (uncomment to test)
    # print("\n=== FULL COORDINATION TEST ===")
    # full_results = coordinate_scrapers(test_domain, "ecommerce_retail")
    # print("Full coordination results:")
    # print(json.dumps(full_results, indent=2))