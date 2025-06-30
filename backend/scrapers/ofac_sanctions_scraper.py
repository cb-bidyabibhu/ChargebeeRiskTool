# backend/scrapers/ofac_sanctions_scraper.py
# NEW SCRAPER - Critical for 2025 compliance

import requests
import xml.etree.ElementTree as ET
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import time

class OFACSanctionsChecker:
    """
    OFAC (Office of Foreign Assets Control) Sanctions List Checker
    Screens companies and individuals against US Treasury sanctions lists
    """
    
    def __init__(self):
        self.base_url = "https://www.treasury.gov/ofac/downloads"
        self.sdn_list_url = f"{self.base_url}/sdn.xml"  # Specially Designated Nationals
        self.alt_list_url = f"{self.base_url}/alt.xml"   # Alternative names
        self.add_list_url = f"{self.base_url}/add.xml"   # Addresses
        
        # Cache for OFAC data (refresh every 24 hours)
        self.cache_duration = 86400  # 24 hours in seconds
        self.cached_data = None
        self.cache_timestamp = None
        
        # User agent for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    
    def check_company_sanctions(self, company_name: str, domain: str = None) -> Dict:
        """
        Main function to check company against OFAC sanctions lists
        
        Args:
            company_name: Company name to check
            domain: Optional domain for additional context
            
        Returns:
            Dict with sanctions screening results
        """
        try:
            print(f"🔍 Checking OFAC sanctions for: {company_name}")
            
            # Load OFAC data
            ofac_data = self._load_ofac_data()
            if not ofac_data:
                return self._create_error_response("Failed to load OFAC data")
            
            # Perform comprehensive screening
            screening_results = self._screen_entity(company_name, domain, ofac_data)
            
            # Format final response
            result = self._format_screening_response(screening_results, company_name, domain)
            
            print(f"✅ OFAC screening completed for {company_name}")
            return result
            
        except Exception as e:
            print(f"❌ OFAC screening failed for {company_name}: {e}")
            return self._create_error_response(str(e))
    
    def _load_ofac_data(self) -> Optional[Dict]:
        """Load and cache OFAC sanctions data"""
        
        # Check if we have valid cached data
        if self._is_cache_valid():
            return self.cached_data
        
        print("📡 Downloading latest OFAC sanctions data...")
        
        try:
            # Download SDN (Specially Designated Nationals) list
            sdn_data = self._download_sdn_list()
            
            # Download alternative names list
            alt_data = self._download_alt_list()
            
            # Combine data
            ofac_data = {
                "sdn_entries": sdn_data,
                "alternative_names": alt_data,
                "download_timestamp": datetime.now().isoformat(),
                "total_entries": len(sdn_data)
            }
            
            # Cache the data
            self.cached_data = ofac_data
            self.cache_timestamp = time.time()
            
            print(f"✅ OFAC data loaded: {len(sdn_data)} entries")
            return ofac_data
            
        except Exception as e:
            print(f"❌ Failed to load OFAC data: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached OFAC data is still valid"""
        if not self.cached_data or not self.cache_timestamp:
            return False
        
        return (time.time() - self.cache_timestamp) < self.cache_duration
    
    def _download_sdn_list(self) -> List[Dict]:
        """Download and parse SDN (Specially Designated Nationals) list"""
        try:
            response = requests.get(self.sdn_list_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            sdn_entries = []
            for entry in root.findall('.//sdnEntry'):
                sdn_entry = self._parse_sdn_entry(entry)
                if sdn_entry:
                    sdn_entries.append(sdn_entry)
            
            return sdn_entries
            
        except Exception as e:
            print(f"❌ Failed to download SDN list: {e}")
            return []
    
    def _download_alt_list(self) -> List[Dict]:
        """Download and parse alternative names list"""
        try:
            response = requests.get(self.alt_list_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            alt_entries = []
            for entry in root.findall('.//altName'):
                alt_entry = self._parse_alt_entry(entry)
                if alt_entry:
                    alt_entries.append(alt_entry)
            
            return alt_entries
            
        except Exception as e:
            print(f"❌ Failed to download alternative names list: {e}")
            return []
    
    def _parse_sdn_entry(self, entry) -> Optional[Dict]:
        """Parse individual SDN entry from XML"""
        try:
            uid = entry.get('uid')
            sdn_type = entry.get('sdnType')
            
            # Extract names
            first_name = entry.findtext('.//firstName', '').strip()
            last_name = entry.findtext('.//lastName', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            # For entities, get the entity name
            entity_name = ""
            for name_elem in entry.findall('.//name'):
                entity_name = name_elem.text.strip() if name_elem.text else ""
                break
            
            # Use entity name if available, otherwise use full name
            primary_name = entity_name if entity_name else full_name
            
            if not primary_name:
                return None
            
            # Extract program information
            programs = []
            for program in entry.findall('.//program'):
                programs.append(program.text.strip() if program.text else "")
            
            # Extract remarks
            remarks = entry.findtext('.//remarks', '').strip()
            
            return {
                "uid": uid,
                "type": sdn_type,
                "primary_name": primary_name,
                "first_name": first_name,
                "last_name": last_name,
                "entity_name": entity_name,
                "programs": programs,
                "remarks": remarks,
                "list_type": "SDN"
            }
            
        except Exception as e:
            print(f"⚠️ Failed to parse SDN entry: {e}")
            return None
    
    def _parse_alt_entry(self, entry) -> Optional[Dict]:
        """Parse alternative name entry from XML"""
        try:
            uid = entry.get('uid')
            alt_type = entry.get('type', '')
            alt_name = entry.text.strip() if entry.text else ""
            
            if not alt_name:
                return None
            
            return {
                "uid": uid,
                "alternative_name": alt_name,
                "type": alt_type,
                "list_type": "Alternative"
            }
            
        except Exception as e:
            print(f"⚠️ Failed to parse alternative name entry: {e}")
            return None
    
    def _screen_entity(self, company_name: str, domain: str, ofac_data: Dict) -> Dict:
        """Perform comprehensive entity screening"""
        
        screening_results = {
            "exact_matches": [],
            "partial_matches": [],
            "domain_matches": [],
            "fuzzy_matches": [],
            "total_matches": 0,
            "risk_level": "CLEAR",
            "screening_timestamp": datetime.now().isoformat()
        }
        
        # Prepare search terms
        search_terms = self._prepare_search_terms(company_name, domain)
        
        # Screen against SDN list
        sdn_matches = self._screen_against_list(search_terms, ofac_data["sdn_entries"], "SDN")
        screening_results["exact_matches"].extend(sdn_matches["exact"])
        screening_results["partial_matches"].extend(sdn_matches["partial"])
        screening_results["fuzzy_matches"].extend(sdn_matches["fuzzy"])
        
        # Screen against alternative names
        alt_matches = self._screen_against_alt_names(search_terms, ofac_data["alternative_names"])
        screening_results["exact_matches"].extend(alt_matches["exact"])
        screening_results["partial_matches"].extend(alt_matches["partial"])
        
        # Domain-specific screening
        if domain:
            domain_matches = self._screen_domain(domain, ofac_data)
            screening_results["domain_matches"] = domain_matches
        
        # Calculate total matches and risk level
        total_matches = (len(screening_results["exact_matches"]) + 
                        len(screening_results["partial_matches"]) + 
                        len(screening_results["domain_matches"]) + 
                        len(screening_results["fuzzy_matches"]))
        
        screening_results["total_matches"] = total_matches
        screening_results["risk_level"] = self._determine_risk_level(screening_results)
        
        return screening_results
    
    def _prepare_search_terms(self, company_name: str, domain: str = None) -> List[str]:
        """Prepare various search terms for comprehensive screening"""
        search_terms = []
        
        # Add original company name
        search_terms.append(company_name.strip())
        
        # Add variations
        # Remove common suffixes
        name_without_suffixes = re.sub(r'\b(Inc|LLC|Corp|Corporation|Company|Co|Ltd|Limited)\b\.?', '', company_name, flags=re.IGNORECASE).strip()
        if name_without_suffixes and name_without_suffixes != company_name:
            search_terms.append(name_without_suffixes)
        
        # Add domain-based variations
        if domain:
            domain_name = domain.split('.')[0]
            search_terms.append(domain_name.capitalize())
            search_terms.append(domain_name.upper())
        
        # Remove duplicates and empty strings
        search_terms = list(set([term for term in search_terms if term.strip()]))
        
        return search_terms
    
    def _screen_against_list(self, search_terms: List[str], sdn_list: List[Dict], list_type: str) -> Dict:
        """Screen search terms against SDN list"""
        matches = {
            "exact": [],
            "partial": [],
            "fuzzy": []
        }
        
        for entry in sdn_list:
            for search_term in search_terms:
                # Exact match
                if self._is_exact_match(search_term, entry):
                    matches["exact"].append({
                        "search_term": search_term,
                        "matched_name": entry.get("primary_name", ""),
                        "uid": entry.get("uid", ""),
                        "programs": entry.get("programs", []),
                        "remarks": entry.get("remarks", ""),
                        "match_type": "exact",
                        "list_type": list_type
                    })
                
                # Partial match
                elif self._is_partial_match(search_term, entry):
                    matches["partial"].append({
                        "search_term": search_term,
                        "matched_name": entry.get("primary_name", ""),
                        "uid": entry.get("uid", ""),
                        "programs": entry.get("programs", []),
                        "remarks": entry.get("remarks", ""),
                        "match_type": "partial",
                        "list_type": list_type
                    })
                
                # Fuzzy match (for high-risk scenarios)
                elif self._is_fuzzy_match(search_term, entry):
                    matches["fuzzy"].append({
                        "search_term": search_term,
                        "matched_name": entry.get("primary_name", ""),
                        "uid": entry.get("uid", ""),
                        "programs": entry.get("programs", []),
                        "remarks": entry.get("remarks", ""),
                        "match_type": "fuzzy",
                        "list_type": list_type
                    })
        
        return matches
    
    def _screen_against_alt_names(self, search_terms: List[str], alt_list: List[Dict]) -> Dict:
        """Screen against alternative names list"""
        matches = {
            "exact": [],
            "partial": []
        }
        
        for alt_entry in alt_list:
            alt_name = alt_entry.get("alternative_name", "")
            
            for search_term in search_terms:
                if self._is_exact_text_match(search_term, alt_name):
                    matches["exact"].append({
                        "search_term": search_term,
                        "matched_name": alt_name,
                        "uid": alt_entry.get("uid", ""),
                        "match_type": "exact",
                        "list_type": "Alternative Names"
                    })
                elif self._is_partial_text_match(search_term, alt_name):
                    matches["partial"].append({
                        "search_term": search_term,
                        "matched_name": alt_name,
                        "uid": alt_entry.get("uid", ""),
                        "match_type": "partial",
                        "list_type": "Alternative Names"
                    })
        
        return matches
    
    def _screen_domain(self, domain: str, ofac_data: Dict) -> List[Dict]:
        """Screen domain against OFAC data"""
        domain_matches = []
        
        # Extract domain name for screening
        domain_name = domain.split('.')[0]
        
        # Screen domain name against entities
        for entry in ofac_data["sdn_entries"]:
            entry_name = entry.get("primary_name", "").lower()
            if domain_name.lower() in entry_name or entry_name in domain_name.lower():
                domain_matches.append({
                    "domain": domain,
                    "matched_name": entry.get("primary_name", ""),
                    "uid": entry.get("uid", ""),
                    "programs": entry.get("programs", []),
                    "match_type": "domain_related"
                })
        
        return domain_matches
    
    def _is_exact_match(self, search_term: str, entry: Dict) -> bool:
        """Check for exact name match"""
        entry_name = entry.get("primary_name", "").lower().strip()
        search_name = search_term.lower().strip()
        
        return entry_name == search_name
    
    def _is_partial_match(self, search_term: str, entry: Dict) -> bool:
        """Check for partial name match"""
        entry_name = entry.get("primary_name", "").lower().strip()
        search_name = search_term.lower().strip()
        
        # Avoid matching very short terms
        if len(search_name) < 4:
            return False
        
        return search_name in entry_name or entry_name in search_name
    
    def _is_fuzzy_match(self, search_term: str, entry: Dict) -> bool:
        """Check for fuzzy/similarity match"""
        entry_name = entry.get("primary_name", "").lower().strip()
        search_name = search_term.lower().strip()
        
        # Simple fuzzy matching - check for word overlap
        search_words = set(search_name.split())
        entry_words = set(entry_name.split())
        
        if len(search_words) == 0 or len(entry_words) == 0:
            return False
        
        # If 50% or more words match, consider it a fuzzy match
        common_words = search_words.intersection(entry_words)
        return len(common_words) >= len(search_words) * 0.5
    
    def _is_exact_text_match(self, search_term: str, text: str) -> bool:
        """Exact text matching for alternative names"""
        return search_term.lower().strip() == text.lower().strip()
    
    def _is_partial_text_match(self, search_term: str, text: str) -> bool:
        """Partial text matching for alternative names"""
        search_lower = search_term.lower().strip()
        text_lower = text.lower().strip()
        
        if len(search_lower) < 4:
            return False
        
        return search_lower in text_lower or text_lower in search_lower
    
    def _determine_risk_level(self, screening_results: Dict) -> str:
        """Determine overall risk level based on screening results"""
        
        exact_matches = len(screening_results["exact_matches"])
        partial_matches = len(screening_results["partial_matches"])
        domain_matches = len(screening_results["domain_matches"])
        fuzzy_matches = len(screening_results["fuzzy_matches"])
        
        # Any exact match = HIGH RISK
        if exact_matches > 0:
            return "HIGH_RISK"
        
        # Multiple partial matches = MEDIUM RISK
        if partial_matches > 2 or domain_matches > 0:
            return "MEDIUM_RISK"
        
        # Some partial or fuzzy matches = LOW RISK
        if partial_matches > 0 or fuzzy_matches > 0:
            return "LOW_RISK"
        
        # No matches = CLEAR
        return "CLEAR"
    
    def _format_screening_response(self, screening_results: Dict, company_name: str, domain: str) -> Dict:
        """Format the final screening response"""
        
        risk_level = screening_results["risk_level"]
        total_matches = screening_results["total_matches"]
        
        return {
            "company_name": company_name,
            "domain": domain,
            "sanctions_screening": {
                "risk_level": risk_level,
                "status": "SANCTIONED" if risk_level == "HIGH_RISK" else "CLEAR",
                "total_matches": total_matches,
                "exact_matches": len(screening_results["exact_matches"]),
                "partial_matches": len(screening_results["partial_matches"]),
                "domain_matches": len(screening_results["domain_matches"]),
                "fuzzy_matches": len(screening_results["fuzzy_matches"])
            },
            "match_details": {
                "exact_matches": screening_results["exact_matches"][:5],  # Limit to top 5
                "partial_matches": screening_results["partial_matches"][:5],
                "domain_matches": screening_results["domain_matches"][:3],
                "high_confidence_matches": [
                    match for match in screening_results["exact_matches"] + screening_results["partial_matches"]
                    if match.get("match_type") in ["exact", "partial"]
                ][:3]
            },
            "compliance_assessment": {
                "ofac_compliant": risk_level == "CLEAR",
                "requires_enhanced_due_diligence": risk_level in ["HIGH_RISK", "MEDIUM_RISK"],
                "immediate_escalation_required": risk_level == "HIGH_RISK",
                "recommendation": self._get_compliance_recommendation(risk_level)
            },
            "metadata": {
                "screening_timestamp": screening_results["screening_timestamp"],
                "ofac_data_version": "Latest",
                "screening_method": "comprehensive",
                "confidence_level": "high" if total_matches == 0 else "medium"
            }
        }
    
    def _get_compliance_recommendation(self, risk_level: str) -> str:
        """Get compliance recommendation based on risk level"""
        recommendations = {
            "CLEAR": "Proceed with standard due diligence procedures",
            "LOW_RISK": "Conduct enhanced due diligence and document findings",
            "MEDIUM_RISK": "Require additional documentation and senior approval",
            "HIGH_RISK": "Prohibit transaction - immediate escalation required"
        }
        
        return recommendations.get(risk_level, "Review required")
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            "error": error_message,
            "sanctions_screening": {
                "status": "ERROR",
                "risk_level": "UNKNOWN"
            },
            "compliance_assessment": {
                "ofac_compliant": False,
                "requires_manual_review": True
            },
            "metadata": {
                "screening_timestamp": datetime.now().isoformat(),
                "error_type": "screening_failure"
            }
        }

# Main function for integration with existing scraper infrastructure
def check_ofac_sanctions(company_name: str, domain: str = None) -> Dict:
    """
    Main function to check OFAC sanctions - use this in your scraper coordination
    
    Args:
        company_name: Company name to screen
        domain: Optional domain for additional context
        
    Returns:
        Dict with comprehensive sanctions screening results
    """
    checker = OFACSanctionsChecker()
    return checker.check_company_sanctions(company_name, domain)

# Test function
if __name__ == "__main__":
    # Test with a known clear company
    test_company = "Shopify"
    test_domain = "shopify.com"
    
    print("Testing OFAC sanctions screening...")
    result = check_ofac_sanctions(test_company, test_domain)
    
    print(f"\nResults for {test_company}:")
    print(f"Status: {result.get('sanctions_screening', {}).get('status')}")
    print(f"Risk Level: {result.get('sanctions_screening', {}).get('risk_level')}")
    print(f"Total Matches: {result.get('sanctions_screening', {}).get('total_matches')}")
    print(f"OFAC Compliant: {result.get('compliance_assessment', {}).get('ofac_compliant')}")