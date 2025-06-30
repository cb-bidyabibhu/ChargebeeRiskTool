test


# import requests

# def get_company_info(domain_name):
#     # Example using UK Companies House API
#     API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
#     company_lookup_url = f"https://api.company-information.service.gov.uk/search/companies?q={domain_name}"
#     headers = {"Authorization": API_KEY}
    
#     try:
#         response = requests.get(company_lookup_url, headers=headers, timeout=5)
#         data = response.json()
        
#         if "items" in data and data["items"]:
#             company = data["items"][0]
#             return {
#                 "domain_name": domain_name,
#                 "company_name": company.get("title"),
#                 "company_number": company.get("company_number"),
#                 "company_status": company.get("company_status"),
#             }
#         return {"domain_name": domain_name, "error": "No company details found"}
#     except Exception as e:
#         return {"domain_name": domain_name, "error": str(e)}

# if __name__ == "__main__":
#     domain_name = input("Enter domain_name: ")
#     result = get_company_info(domain_name)
#     print(result)
