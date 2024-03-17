"""
Utility program to get 'company_tickers_exchange.json' file
"""
import requests

# Used to hide my email
from my_email import hide_email
EMAIL = (hide_email.get("email"))

# required for requests
headers = {
    "User-Agent": "EMAIL",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}


def download_json():
    """
    run once if the file is not in your root directory or file has changed
    Downloads the JSON file of companies, tickers, and CIKs from SEC website:
        url: https://www.sec.gov/files/company_tickers_exchange.json
        saves JSON file as "company_tickers_exchange.json"
    """
    # URL of the JSON file
    url = "https://www.sec.gov/files/company_tickers_exchange.json"

    # Filename to save the JSON data (root directory)
    filename = "company_tickers_exchange.json"

    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the JSON response to a file
        with open(filename, 'w') as file:
            file.write(response.text)
        print(f"JSON file saved as {filename}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")


# Run this once to get json file
download_json()
