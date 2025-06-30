import requests

def check_url_with_urlhaus(url, auth_key):
    api_url = "https://urlhaus-api.abuse.ch/v1/url/"
    headers = {"Auth-Key": auth_key}
    data = {"url": url}
    
    response = requests.post(api_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

if __name__ == "__main__":
    AUTH_KEY = "f914a5e14fe5fe7385b5e15f7c1ec220b6503917ae09a28b"
    URL_TO_CHECK = "https://www.olleyes.com"
    
    result = check_url_with_urlhaus(URL_TO_CHECK, AUTH_KEY)
    print(result)