import requests

def get_lei_and_details(company_name):
    """
    Step 1: Fetches the LEI from the company name.
    Step 2: Uses the LEI to fetch full company details.
    Returns structured JSON output.
    """
    
    # Step 1: Get LEI from company name
    url = "https://api.gleif.org/api/v1/lei-records"
    params = {"filter[entity.legalName]": company_name}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            lei = data["data"][0]["id"]  # Get the first matched LEI
            legal_name = data["data"][0]["attributes"]["entity"]["legalName"]["name"]

            # Step 2: Use LEI to get full company details
            details_url = f"https://api.gleif.org/api/v1/lei-records/{lei}"
            details_response = requests.get(details_url)

            if details_response.status_code == 200:
                full_details = details_response.json()
                return {
                    "company_name": legal_name,
                    "lei": lei,
                    "company_details": full_details["data"]["attributes"]
                }

    return {"error": "LEI or company details not found"}

# Example usage
print(get_lei_and_details("chargebee"))
