# backend/scrapers/mcc_classifier_gemini_final.py
# UPDATED VERSION - Copy this entire content to replace your existing file

import asyncio
import time
import logging
from typing import Dict, Optional
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("⚠️ GOOGLE_API_KEY not found in environment variables")

async def extract_text_from_url_async(url: str, max_retries: int = 2) -> str:
    """
    Extract text content from URL using multiple fallback methods (async-friendly)
    """
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Method 1: Try requests + BeautifulSoup (fastest)
    try:
        logger.info(f"Trying requests for {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        if len(text) > 500:  # Minimum viable content
            logger.info(f"✓ Successfully extracted content using requests")
            return text[:5000]  # Limit to 5000 chars
            
    except Exception as e:
        logger.warning(f"✗ Failed with requests: {e}")
    
    # Method 2: Try Selenium (more reliable for JS-heavy sites)
    try:
        logger.info(f"Trying selenium for {url}")
        return await extract_with_selenium_async(url)
    except Exception as e:
        logger.warning(f"✗ Failed with selenium: {e}")
    
    return f"Failed to extract content from {url}. Website may be inaccessible or protected."

async def extract_with_selenium_async(url: str) -> str:
    """
    Extract content using Selenium in a thread pool to avoid blocking
    """
    def selenium_extract():
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(15)
            driver.implicitly_wait(10)
            
            driver.get(url)
            
            # Wait for basic content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Remove unwanted elements
            unwanted_selectors = [
                'script', 'style', 'nav', 'footer', 'aside', 
                '.advertisement', '.ad', '.popup', '.modal'
            ]
            
            for selector in unwanted_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        driver.execute_script("arguments[0].remove();", element)
                except:
                    pass
            
            # Get text content
            text_content = driver.find_element(By.TAG_NAME, "body").text
            
            # Clean up text
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            text = ' '.join(lines)
            
            return text[:5000] if text else "No content extracted"
            
        finally:
            if driver:
                driver.quit()
    
    # Run selenium in thread pool to avoid blocking async event loop
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, selenium_extract)
    
    if len(text) > 500:
        logger.info(f"✓ Successfully extracted content using selenium")
        return text
    else:
        raise Exception("Insufficient content extracted")

def extract_text_from_url(url: str) -> str:
    """
    Synchronous wrapper for backward compatibility
    """
    try:
        # Check if we're in an async context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, extract_text_from_url_async(url))
                return future.result(timeout=30)
        else:
            # We're not in an async context, run normally
            return asyncio.run(extract_text_from_url_async(url))
    except Exception as e:
        logger.error(f"Failed to extract text from {url}: {e}")
        return f"Failed to extract content from {url}. Error: {str(e)}"

def classify_mcc_using_gemini(domain: str, website_content: str) -> Dict:
    """
    Classify domain into MCC category using Gemini AI
    """
    if not API_KEY:
        return {
            "error": "Gemini API key not configured",
            "mcc_code": "unknown",
            "description": "Cannot classify without API key",
            "confidence": 0.0
        }
    
    try:
        logger.info(f"🤖 Classifying {domain} using Gemini AI")
        
        # Truncate content for prompt
        content_snippet = website_content[:2000] if website_content else "No content available"
        
        prompt = f"""
        Analyze this website domain and content to determine the most appropriate Merchant Category Code (MCC).

        Domain: {domain}
        Website Content: {content_snippet}

        Based on the domain name and website content, classify this business into one of these major MCC categories:

        1. Software/SaaS (MCC: 5734) - Software stores, SaaS platforms, development tools
        2. E-commerce/Retail (MCC: 5969) - Online retail, marketplaces, direct marketing
        3. FinTech/Financial (MCC: 6012) - Financial services, payment processing, banking
        4. Media/Information (MCC: 7372) - Content platforms, information services, media
        5. Healthcare (MCC: 8011) - Medical services, healthcare platforms, telemedicine
        6. Professional Services (MCC: 8999) - Consulting, legal, accounting, business services
        7. Manufacturing (MCC: 5013) - Manufacturing, industrial equipment, supply chain
        8. Other (MCC: 7399) - Miscellaneous services not fitting above categories

        Respond with ONLY a JSON object in this exact format:
        {{
            "mcc_code": "5734",
            "category": "software_saas",
            "description": "Computer Software and SaaS Platforms",
            "confidence": 0.85,
            "reasoning": "Brief explanation of classification"
        }}
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            
            # Validate result
            required_fields = ["mcc_code", "category", "description", "confidence"]
            if all(field in result for field in required_fields):
                logger.info(f"✅ Classification successful: {result['category']} (confidence: {result['confidence']})")
                return result
            else:
                raise ValueError("Missing required fields in AI response")
        else:
            raise ValueError("No valid JSON found in AI response")
            
    except Exception as e:
        logger.error(f"❌ Classification failed for {domain}: {e}")
        return {
            "error": str(e),
            "mcc_code": "7399",
            "category": "other",
            "description": "Classification failed - defaulting to miscellaneous services",
            "confidence": 0.1,
            "reasoning": f"Error occurred during classification: {str(e)}"
        }

# Test function
async def test_classifier():
    """Test the classifier with a sample domain"""
    test_domain = "shopify.com"
    
    print(f"Testing classifier with {test_domain}...")
    
    # Test content extraction
    content = await extract_text_from_url_async(test_domain)
    print(f"Content length: {len(content)}")
    print(f"Content preview: {content[:200]}...")
    
    # Test classification
    result = classify_mcc_using_gemini(test_domain, content)
    print(f"Classification result: {result}")

if __name__ == "__main__":
    asyncio.run(test_classifier())