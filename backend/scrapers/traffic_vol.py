from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def convert_to_number(value):
    """
    Convert traffic values from K/M/B format to numeric.
    Example: "29.81K" -> 29810, "1.2M" -> 1200000
    """
    value = value.strip()  # Remove extra spaces

    if not value:  # If value is empty, return 0
        return 0

    if "K" in value:
        return int(float(value.replace("K", "")) * 1000)
    elif "M" in value:
        return int(float(value.replace("M", "")) * 1000000)
    elif "B" in value:
        return int(float(value.replace("B", "")) * 1000000000)
    
    try:
        return int(value)  # If it's a plain number
    except ValueError:
        return 0  # Return 0 if conversion fails

def check_traffic(domain):
    """
    Scrape website traffic data for a given domain using Selenium.
    """
    url = f"https://xamsor.com/website-traffic-checker/?domain={domain}"

    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--ignore-certificate-errors")  # Bypass SSL certificate errors
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Helps with resource allocation

    # Initialize WebDriver
    service = Service()  # Uses default installed ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for content to load

        # Extract values using HTML structure from screenshot
        last_month_traffic = driver.find_element(By.ID, "traffic_main_value").text
        previous_month_traffic = driver.find_element(By.ID, "traffic_month_ago").text
        year_ago_traffic = driver.find_element(By.ID, "traffic_year_ago").text

        return {
            "domain": domain,
            "last_month_traffic": convert_to_number(last_month_traffic),
            "previous_month_traffic": convert_to_number(previous_month_traffic),
            "year_ago_traffic": convert_to_number(year_ago_traffic)
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.quit()  # Ensure the driver closes

if __name__ == "__main__":
    domain = "chargebee.com"  # Replace with actual domain from main.py
    result = check_traffic(domain)
    print(result)
