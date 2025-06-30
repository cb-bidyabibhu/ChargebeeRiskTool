from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def check_malicious_nordvpn(domain):
    """
    Check if a website is flagged as malicious by NordVPN Link Checker using Selenium.
    """
    url = "https://nordvpn.com/link-checker/"

    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--ignore-certificate-errors")  # Bypass SSL certificate errors
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Helps with resource allocation

    # Initialize WebDriver
    service = Service()  # Use the default installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Wait for the input box to load
        wait = WebDriverWait(driver, 10)
        input_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter your URL here']")))

        # Enter the domain
        input_box.clear()
        input_box.send_keys(domain)
        time.sleep(1)  # Mimic human behavior

        # Wait for the Analyze button and click it
        analyze_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Analyze')]")))
        analyze_button.click()

        # Wait for the result message to appear
        result_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.body-md.whitespace-normal.break-words.-mt-1")))

        result_text = result_element.text.strip() if result_element else "No analysis result found"

        # Determine if the domain is malicious based on extracted text
        if "no signs of malicious activity" in result_text.lower():
            is_malicious = False
        elif "was identified as a phishing site" in result_text.lower():
            is_malicious = True
        else:
            is_malicious = None  # Unknown status

        return {
            "domain": domain,
            "is_malicious_nordvpn": is_malicious,
            "message": result_text
        }

    except Exception as e:
        return {
            "domain": domain,
            "error": str(e)
        }
    finally:
        driver.quit()  # Ensure the driver closes

if __name__ == "__main__":
    domain = "17ebook.com"  # Replace with any domain
    result = check_malicious_nordvpn(domain)
    print(result)
