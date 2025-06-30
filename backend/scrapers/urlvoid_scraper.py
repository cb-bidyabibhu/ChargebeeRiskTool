import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_urlvoid(domain):
    """
    Uses Selenium to interact with multirbl.valli.org, check a domain's blacklist status,
    wait for results, and extract relevant high-level details without blacklisted entries details.
    """
    url = f"https://multirbl.valli.org/lookup/{domain}.html"  # Direct URL for domain lookup

    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--ignore-certificate-errors")  # Ignore SSL warnings
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Improve performance in containers

    # Initialize WebDriver
    service = Service()  # Use an already installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    try:
        # Wait for the results to load (check for the presence of the summary table)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "global_data_cnt_DNSBLBlacklistTest"))
        )

        # Give a bit more time for all tests to complete
        time.sleep(5)

        # Extract page source after the scan completes
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract data from each test category
        result = {
            "domain": domain,
            "blacklist_tests": extract_test_results(soup, "DNSBLBlacklistTest"),
            "combinedlist_tests": extract_test_results(soup, "DNSBLCombinedlistTest"),
            "whitelist_tests": extract_test_results(soup, "DNSBLWhitelistTest"),
            "informationallist_tests": extract_test_results(soup, "DNSBLInformationallistTest")
        }

        return result

    except Exception as e:
        return {"error": f"failed_to_scrape_urlvoid: {str(e)}"}
    
    finally:
        driver.quit()  # Ensure WebDriver is properly closed

def extract_test_results(soup, test_type):
    """
    Extract test results for a specific test type from the page.
    """
    results = {}
    
    # Extract total tests
    total_tests_element = soup.find("span", class_=f"global_data_cnt_{test_type}")
    if total_tests_element:
        results["total_tests"] = int(total_tests_element.text.strip())
    
    # Extract not listed
    not_listed_element = soup.find("span", class_=f"global_data_cntNotlisted_{test_type}")
    if not_listed_element:
        results["not_listed"] = int(not_listed_element.text.strip())
    
    # Extract blacklisted
    blacklisted_element = soup.find("span", class_=f"global_data_cntBlacklisted_{test_type}")
    if blacklisted_element:
        results["blacklisted"] = int(blacklisted_element.text.strip())
    
    # Extract other statuses if needed and present in the original script
    
    return results

if __name__ == "__main__":
    domain = "zmtha.info"  # Replace with the domain to check
    result = scrape_urlvoid(domain)
    print(result)
