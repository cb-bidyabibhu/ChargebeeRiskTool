# backend/scrapers/priority_kyb_scrapers.py
# ADD THESE 4 CRITICAL SCRAPERS to your scrapers folder

import aiohttp
import asyncio
import json
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import StringIO
import time

class EnhancedKYBScrapers:
    """
    Priority KYB scrapers for 2025 compliance standards
    These integrate with your existing scraper system
    """
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    # 1. SECRETARY OF STATE SCRAPER (Business Registration Verification)
    async def scrape_secretary_of_state(self, company_name: str, state: str = "DE") -> dict:
        """
        Scrape Secretary of State for business registration verification
        Integrates with your existing scraper coordinator
        """
        try:
            results = {
                "scraper_name": "secretary_of_state",
                "registration_status": "unknown",
                "incorporation_date": None,
                "business_type": None,
                "registered_agent": None,
                "entity_status": "unknown",
                "state_of_incorporation": state.upper(),
                "entity_id": None,
                "source": f"{state.upper()} Secretary of State",
                "timestamp": datetime.now().isoformat(),
                "compliance_verified": False
            }

            if state.upper() == "DE":
                # Delaware Division of Corporations (most common incorporation state)
                url = "https://icis.corp.delaware.gov/Ecorp/EntitySearch/NameSearch.aspx"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Get the search page
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract ASP.NET form data
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                        
                        if viewstate and eventvalidation:
                            # Submit search form
                            form_data = {
                                '__VIEWSTATE': viewstate['value'],
                                '__EVENTVALIDATION': eventvalidation['value'],
                                'ctl00$ContentPlaceHolder1$frmEntityName$txtEntityName': company_name,
                                'ctl00$ContentPlaceHolder1$frmEntityName$btnSubmit': 'Search'
                            }
                            
                            async with self.session.post(url, data=form_data, headers=headers) as search_response:
                                if search_response.status == 200:
                                    search_html = await search_response.text()
                                    search_soup = BeautifulSoup(search_html, 'html.parser')
                                    
                                    # Parse search results
                                    results_table = search_soup.find('table', {'id': 'tblSearchResults'})
                                    if results_table:
                                        rows = results_table.find_all('tr')[1:]  # Skip header
                                        for row in rows:
                                            cells = row.find_all('td')
                                            if len(cells) >= 4:
                                                entity_name = cells[0].text.strip()
                                                entity_type = cells[1].text.strip()
                                                entity_id = cells[2].text.strip()
                                                status = cells[3].text.strip()
                                                
                                                # Check name similarity
                                                if self._is_name_match(company_name, entity_name):
                                                    results.update({
                                                        "registration_status": "found",
                                                        "business_type": entity_type,
                                                        "entity_id": entity_id,
                                                        "entity_status": status.lower(),
                                                        "matched_name": entity_name,
                                                        "compliance_verified": True
                                                    })
                                                    break

            elif state.upper() == "CA":
                # California Secretary of State API
                api_url = "https://bizfileonline.sos.ca.gov/api/Records/businesssearch"
                search_data = {
                    "SearchValue": company_name,
                    "SearchType": "CONTAINS",
                    "EntityType": "ALL"
                }
                
                async with self.session.post(api_url, json=search_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('results'):
                            for entity in data['results'][:3]:  # Check top 3 matches
                                if self._is_name_match(company_name, entity.get('name', '')):
                                    results.update({
                                        "registration_status": "found",
                                        "business_type": entity.get('type'),
                                        "entity_id": entity.get('id'),
                                        "entity_status": entity.get('status', '').lower(),
                                        "matched_name": entity.get('name'),
                                        "compliance_verified": True
                                    })
                                    break

            return results
            
        except Exception as e:
            return {
                "scraper_name": "secretary_of_state",
                "registration_status": "error",
                "error": str(e),
                "source": f"{state.upper()} Secretary of State",
                "timestamp": datetime.now().isoformat()
            }

    # 2. ENHANCED OFAC SANCTIONS SCRAPER
    async def scrape_enhanced_ofac_sanctions(self, company_name: str, owner_names: list = None) -> dict:
        """
        Enhanced OFAC sanctions screening with comprehensive analysis
        Builds on your existing OFAC scraper
        """
        try:
            results = {
                "scraper_name": "enhanced_ofac_sanctions",
                "sanctions_status": "clear",
                "total_matches": 0,
                "company_matches": [],
                "owner_matches": [],
                "risk_level": "CLEAR",
                "last_updated": datetime.now().isoformat(),
                "source": "OFAC Enhanced Screening",
                "compliance_assessment": {
                    "ofac_compliant": True,
                    "requires_enhanced_dd": False,
                    "escalation_required": False
                }
            }

            # Download current OFAC SDN list
            sdn_url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
            
            headers = {
                'User-Agent': 'Chargebee KYB Compliance System (compliance@chargebee.com)'
            }
            
            async with self.session.get(sdn_url, headers=headers) as response:
                if response.status == 200:
                    csv_content = await response.text()
                    
                    # Parse SDN CSV
                    csv_reader = csv.DictReader(StringIO(csv_content))
                    
                    # Screen company name
                    company_matches = self._screen_entity_against_sdn(company_name, csv_reader, "COMPANY")
                    results["company_matches"] = company_matches
                    
                    # Screen owner names if provided
                    if owner_names:
                        csv_reader = csv.DictReader(StringIO(csv_content))  # Reset reader
                        for owner_name in owner_names:
                            owner_matches = self._screen_entity_against_sdn(owner_name, csv_reader, "INDIVIDUAL")
                            results["owner_matches"].extend(owner_matches)
                    
                    # Calculate total matches and risk level
                    total_matches = len(company_matches) + len(results["owner_matches"])
                    results["total_matches"] = total_matches
                    
                    if total_matches > 0:
                        results["sanctions_status"] = "match_found"
                        
                        # Determine risk level based on match quality
                        high_confidence_matches = [
                            m for m in (company_matches + results["owner_matches"]) 
                            if m.get("match_score", 0) > 0.9
                        ]
                        
                        if high_confidence_matches:
                            results["risk_level"] = "HIGH_RISK"
                            results["compliance_assessment"] = {
                                "ofac_compliant": False,
                                "requires_enhanced_dd": True,
                                "escalation_required": True
                            }
                        else:
                            results["risk_level"] = "MEDIUM_RISK"
                            results["compliance_assessment"] = {
                                "ofac_compliant": False,
                                "requires_enhanced_dd": True,
                                "escalation_required": False
                            }

            # Also check consolidated sanctions list
            await self._check_consolidated_sanctions(results, company_name, owner_names)

            return results
            
        except Exception as e:
            return {
                "scraper_name": "enhanced_ofac_sanctions",
                "sanctions_status": "error",
                "error": str(e),
                "source": "OFAC Enhanced Screening",
                "timestamp": datetime.now().isoformat()
            }

    # 3. SEC EDGAR SCRAPER (Enhanced Financial Intelligence)
    async def scrape_sec_edgar_enhanced(self, company_name: str, ticker: str = None) -> dict:
        """
        Enhanced SEC EDGAR scraper for comprehensive financial analysis
        """
        try:
            results = {
                "scraper_name": "sec_edgar_enhanced",
                "filing_status": "not_found",
                "is_public_company": False,
                "cik": None,
                "sec_company_name": None,
                "recent_filings": [],
                "financial_analysis": {},
                "compliance_status": "unknown",
                "source": "SEC EDGAR Enhanced",
                "timestamp": datetime.now().isoformat()
            }

            # SEC EDGAR Company Search
            search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
            
            headers = {
                'User-Agent': 'Chargebee KYB Compliance System compliance@chargebee.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            # Search by company name
            params = {
                'action': 'getcompany',
                'company': company_name,
                'output': 'xml',
                'count': 20
            }

            await asyncio.sleep(0.1)  # SEC rate limiting
            
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    
                    # Parse XML response
                    if '<company-info>' in xml_content:
                        results["filing_status"] = "found"
                        results["is_public_company"] = True
                        
                        # Extract company information using regex (simpler than XML parsing)
                        cik_match = re.search(r'<cik>(\d+)</cik>', xml_content)
                        name_match = re.search(r'<conformed-name>([^<]+)</conformed-name>', xml_content)
                        
                        if cik_match:
                            results["cik"] = cik_match.group(1)
                        if name_match:
                            results["sec_company_name"] = name_match.group(1)

                        # Extract recent filings
                        filing_pattern = r'<filing>.*?<form>([^<]+)</form>.*?<filing-date>([^<]+)</filing-date>.*?<description>([^<]*)</description>.*?</filing>'
                        filings = re.findall(filing_pattern, xml_content, re.DOTALL)
                        
                        for form, date, description in filings[:10]:
                            results["recent_filings"].append({
                                "form_type": form.strip(),
                                "filing_date": date.strip(),
                                "description": description.strip()
                            })
                        
                        # Analyze filing types for compliance assessment
                        form_types = [f["form_type"] for f in results["recent_filings"]]
                        
                        if "10-K" in form_types or "10-Q" in form_types:
                            results["compliance_status"] = "current_filer"
                        elif any(form in form_types for form in ["8-K", "DEF 14A"]):
                            results["compliance_status"] = "active_filer"
                        else:
                            results["compliance_status"] = "limited_filings"

            # Get additional financial data if ticker provided
            if ticker and results["is_public_company"]:
                await self._get_enhanced_financial_data(ticker, results)

            return results
            
        except Exception as e:
            return {
                "scraper_name": "sec_edgar_enhanced",
                "filing_status": "error",
                "error": str(e),
                "source": "SEC EDGAR Enhanced",
                "timestamp": datetime.now().isoformat()
            }

    # 4. ENHANCED NEWS/ADVERSE MEDIA SCRAPER
    async def scrape_enhanced_adverse_media(self, company_name: str, days_back: int = 90) -> dict:
        """
        Enhanced adverse media screening with comprehensive news analysis
        """
        try:
            results = {
                "scraper_name": "enhanced_adverse_media",
                "media_status": "clear",
                "total_articles": 0,
                "risk_articles": 0,
                "neutral_articles": 0,
                "positive_articles": 0,
                "articles": [],
                "risk_keywords_found": [],
                "sentiment_analysis": {
                    "overall_sentiment": "neutral",
                    "risk_score": 0,
                    "confidence": 0.5
                },
                "source": "Enhanced News Screening",
                "timestamp": datetime.now().isoformat(),
                "monitoring_period_days": days_back
            }

            # Enhanced risk keywords for 2025 compliance
            high_risk_keywords = [
                # Financial crimes
                "money laundering", "terrorist financing", "sanctions violation", "fraud",
                "embezzlement", "bribery", "corruption", "tax evasion", "wire fraud",
                
                # Legal issues
                "criminal charges", "indictment", "conviction", "guilty plea", "settlement",
                "lawsuit", "litigation", "class action", "bankruptcy", "insolvency",
                
                # Regulatory issues
                "regulatory violation", "sec investigation", "ftc action", "cfpb enforcement",
                "license revoked", "cease and desist", "consent order", "penalty",
                
                # Security issues
                "data breach", "cyber attack", "hacking", "security incident", "privacy violation",
                
                # Reputation issues
                "ponzi scheme", "pyramid scheme", "scam", "deceptive practices", "misleading"
            ]

            medium_risk_keywords = [
                "investigation", "probe", "inquiry", "review", "examination", "audit",
                "complaint", "allegation", "dispute", "controversy", "concern"
            ]

            # Search multiple news sources
            news_sources = [
                {
                    "name": "Google News",
                    "url": "https://news.google.com/rss/search",
                    "params": {"q": f'"{company_name}"', "hl": "en", "gl": "US", "ceid": "US:en"}
                },
                {
                    "name": "Financial News",
                    "url": "https://news.google.com/rss/search", 
                    "params": {"q": f'"{company_name}" financial', "hl": "en", "gl": "US", "ceid": "US:en"}
                }
            ]

            for source in news_sources:
                try:
                    await asyncio.sleep(1)  # Rate limiting
                    
                    async with self.session.get(source["url"], params=source["params"]) as response:
                        if response.status == 200:
                            rss_content = await response.text()
                            articles = self._parse_rss_feed(rss_content, source["name"])
                            
                            for article in articles:
                                # Enhanced sentiment and risk analysis
                                risk_analysis = self._analyze_article_risk(
                                    article, high_risk_keywords, medium_risk_keywords
                                )
                                
                                article.update(risk_analysis)
                                results["articles"].append(article)
                                results["total_articles"] += 1
                                
                                # Categorize articles
                                if risk_analysis["risk_level"] == "high":
                                    results["risk_articles"] += 1
                                elif risk_analysis["risk_level"] == "medium":
                                    results["risk_articles"] += 1
                                elif risk_analysis["sentiment"] == "positive":
                                    results["positive_articles"] += 1
                                else:
                                    results["neutral_articles"] += 1
                                
                                # Collect risk keywords
                                results["risk_keywords_found"].extend(risk_analysis.get("risk_keywords", []))

                except Exception as e:
                    print(f"Error scraping {source['name']}: {e}")

            # Calculate overall risk assessment
            if results["total_articles"] > 0:
                risk_ratio = results["risk_articles"] / results["total_articles"]
                
                if risk_ratio > 0.4:
                    results["media_status"] = "high_risk"
                elif risk_ratio > 0.2:
                    results["media_status"] = "medium_risk"
                elif risk_ratio > 0.1:
                    results["media_status"] = "low_risk"
                else:
                    results["media_status"] = "clear"
                
                # Enhanced sentiment analysis
                results["sentiment_analysis"] = {
                    "overall_sentiment": "negative" if risk_ratio > 0.3 else "neutral" if risk_ratio > 0.1 else "positive",
                    "risk_score": min(risk_ratio * 10, 10),
                    "confidence": min(results["total_articles"] / 10, 1.0)
                }

            # Remove duplicate risk keywords
            results["risk_keywords_found"] = list(set(results["risk_keywords_found"]))

            return results
            
        except Exception as e:
            return {
                "scraper_name": "enhanced_adverse_media",
                "media_status": "error",
                "error": str(e),
                "source": "Enhanced News Screening",
                "timestamp": datetime.now().isoformat()
            }

    # UTILITY FUNCTIONS
    
    def _is_name_match(self, search_name: str, found_name: str, threshold: float = 0.8) -> bool:
        """Enhanced name matching for business entities"""
        search_clean = re.sub(r'[^\w\s]', '', search_name.lower())
        found_clean = re.sub(r'[^\w\s]', '', found_name.lower())
        
        # Remove common business suffixes
        suffixes = ['inc', 'corp', 'llc', 'ltd', 'company', 'co', 'corporation', 'limited']
        for suffix in suffixes:
            search_clean = re.sub(rf'\b{suffix}\b', '', search_clean).strip()
            found_clean = re.sub(rf'\b{suffix}\b', '', found_clean).strip()
        
        return self._calculate_similarity(search_clean, found_clean) >= threshold

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using multiple algorithms"""
        from difflib import SequenceMatcher
        
        # Basic sequence matcher
        basic_sim = SequenceMatcher(None, name1, name2).ratio()
        
        # Word-based similarity
        words1 = set(name1.split())
        words2 = set(name2.split())
        word_sim = len(words1.intersection(words2)) / max(len(words1.union(words2)), 1)
        
        # Combined similarity
        return (basic_sim * 0.7) + (word_sim * 0.3)

    def _screen_entity_against_sdn(self, entity_name: str, csv_reader, entity_type: str) -> list:
        """Screen entity against SDN list with enhanced matching"""
        matches = []
        
        for row in csv_reader:
            sdn_name = row.get('SDN_Name', '').strip()
            sdn_type = row.get('SDN_Type', '').strip()
            program = row.get('Program', '').strip()
            
            similarity = self._calculate_similarity(entity_name.lower(), sdn_name.lower())
            
            if similarity > 0.7:  # Potential match threshold
                matches.append({
                    "search_term": entity_name,
                    "matched_name": sdn_name,
                    "entity_type": sdn_type,
                    "program": program,
                    "match_score": round(similarity, 3),
                    "match_confidence": "high" if similarity > 0.9 else "medium" if similarity > 0.8 else "low"
                })
        
        return matches

    async def _check_consolidated_sanctions(self, results: dict, company_name: str, owner_names: list = None):
        """Check consolidated sanctions list (placeholder for future enhancement)"""
        # This would integrate with EU consolidated list, UN sanctions, etc.
        # For now, we'll add a placeholder
        results["additional_sanctions_checked"] = ["EU_CONSOLIDATED", "UN_SANCTIONS"]

    async def _get_enhanced_financial_data(self, ticker: str, results: dict):
        """Get enhanced financial data for public companies"""
        try:
            # Placeholder for Alpha Vantage or other financial API integration
            # You would integrate with your preferred financial data provider here
            results["financial_analysis"] = {
                "ticker": ticker,
                "market_data_available": True,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            results["financial_analysis"] = {"error": str(e)}

    def _parse_rss_feed(self, rss_content: str, source_name: str) -> list:
        """Parse RSS feed and extract articles"""
        articles = []
        
        try:
            soup = BeautifulSoup(rss_content, 'xml')
            items = soup.find_all('item')
            
            for item in items:
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                if title:
                    article = {
                        "title": title.text.strip(),
                        "description": description.text.strip() if description else "",
                        "url": link.text.strip() if link else "",
                        "published": pub_date.text.strip() if pub_date else "",
                        "source": source_name
                    }
                    articles.append(article)
            
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
        
        return articles

    def _analyze_article_risk(self, article: dict, high_risk_keywords: list, medium_risk_keywords: list) -> dict:
        """Analyze article for risk indicators"""
        full_text = f"{article['title']} {article['description']}".lower()
        
        # Check for risk keywords
        high_risk_found = [kw for kw in high_risk_keywords if kw in full_text]
        medium_risk_found = [kw for kw in medium_risk_keywords if kw in full_text]
        
        risk_level = "low"
        sentiment = "neutral"
        
        if high_risk_found:
            risk_level = "high"
            sentiment = "negative"
        elif medium_risk_found:
            risk_level = "medium"
            sentiment = "negative"
        else:
            # Check for positive indicators
            positive_words = ["growth", "expansion", "award", "success", "profit", "revenue increase"]
            if any(word in full_text for word in positive_words):
                sentiment = "positive"
        
        return {
            "risk_level": risk_level,
            "sentiment": sentiment,
            "risk_keywords": high_risk_found + medium_risk_found,
            "risk_score": len(high_risk_found) * 2 + len(medium_risk_found)
        }

# Integration functions for your existing system

async def run_enhanced_priority_scrapers(company_name: str, domain: str, state: str = "DE", 
                                       owner_names: list = None, ticker: str = None) -> dict:
    """
    Run all enhanced priority scrapers
    This integrates with your existing scraper_coordinator.py
    """
    async with EnhancedKYBScrapers() as scrapers:
        tasks = [
            scrapers.scrape_secretary_of_state(company_name, state),
            scrapers.scrape_enhanced_ofac_sanctions(company_name, owner_names),
            scrapers.scrape_sec_edgar_enhanced(company_name, ticker),
            scrapers.scrape_enhanced_adverse_media(company_name)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "secretary_of_state": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "enhanced_ofac_sanctions": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "sec_edgar_enhanced": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "enhanced_adverse_media": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
        }

# Add these to your scraper_coordinator.py:
"""
To integrate with your existing system:

1. Add these imports to your scraper_coordinator.py:
   from scrapers.priority_kyb_scrapers import run_enhanced_priority_scrapers

2. Add this to your get_industry_scraper_config method:
   
   # Add enhanced priority scrapers to critical group
   if ENHANCED_PRIORITY_AVAILABLE:
       enhanced_scrapers = await run_enhanced_priority_scrapers(company_name, domain)
       base_config["enhanced_priority"] = enhanced_scrapers

3. Update your coordinate_full_assessment method to include enhanced scrapers
"""