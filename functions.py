import os
import pandas as pd
import json
import requests
import pdfkit

headers = {
    "User-Agent": "larsondg2000@gmail.com",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}


def download_json():
    """
    run once
    Download the JSON file of companies, tickers, and CIKs from SEC website:
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


def user_input():
    """

    :return:
    """
    while True:
        # User inputs the ticker, report type, and years
        ticker = input("Please enter the stock ticker (ex. MSFT): ").upper()
        report = input("Please enter the report (10-K or 10-Q): ").upper()
        num_reports = int(input("Please enter the number of report: "))

        # Confirm inputs are correct
        if report == "10-K":
            confirm_10k = input(f"Please confirm: \n "
                                f"You would like {num_reports} 10-K report_folder for {ticker} (Y or N): ").upper()
            if confirm_10k == "Y":
                print(f"Ok, getting ({num_reports}) annual report for ticker {ticker}.")
                break
            else:
                print("Ok, please input your choices again:")

        elif report == "10-Q":
            confirm_10q = input(f"Please confirm: \n "
                                f"You would like {num_reports} 10-Q report for {ticker} (Y or N): ").upper()
            if confirm_10q == "Y":
                print(f"Ok, getting ({num_reports}) quarterly report for ticker {ticker}.")
                break
            else:
                print("Ok, please input your choices again:")
        else:
            print("You entered an invalid parameters, please re-enter your inputs:")

    return ticker, report, num_reports


def ticker_to_cik(ticker):
    """

    :param ticker:
    :return:
    """
    # load the saved JSON file
    with open("company_tickers_exchange.json", "r") as f:
        cik_dict = json.load(f)

    # Convert cik_dict to pandas
    cik_df = pd.DataFrame(cik_dict["data"], columns=cik_dict["fields"])

    # get the CIK value for the corresponding ticker
    cik = cik_df[cik_df["ticker"] == ticker].cik.values[0]

    # Get current filing history url using the CIK,
    # Note CIK needs to be 10-digits so zfill pads the CIK value with zeros
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"

    return cik, url


def filings_to_df(url):
    """

    :param url:
    :return:
    """
    # initialize pandas df
    company_filings_df = pd.DataFrame()

    try:
        # read response from REST API with `requests` library and format it as python dict
        company_filings = requests.get(url, headers=headers)
        company_filings.raise_for_status()  # Raise an exception for HTTP errors

        # Use the json module to load response into a dictionary.
        company_filings_dict = json.loads(company_filings.text)

        # Convert dictionary to pandas
        company_filings_df = pd.DataFrame(company_filings_dict["filings"]["recent"])

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")

    return company_filings_df


def filter_reports(company_filings_df, report):
    """

    :param company_filings_df:
    :param report:
    :return:
    """
    # Filter to get just 10-K or 10-Q df
    if report == "10-K":
        report_filtered = company_filings_df[company_filings_df.form == "10-K"]
        return report_filtered
    elif report == "10-Q":
        report_filtered = company_filings_df[company_filings_df.form == "10-Q"]
        return report_filtered
    else:
        print("Invalid Report")


def access_reports(reports_filtered, num_reports, cik, output_folder):
    """

    :param reports_filtered:
    :param num_reports:
    :param cik:
    :param output_folder:
    :return:
    """
    # get the number of report_folder from the filtered df
    report_length = len(reports_filtered)

    # if there are fewer report_folder than requested, set the index to the number of report_folder available
    if num_reports > report_length:
        idx = report_length
    else:
        idx = num_reports

    for i in range(0, idx):
        access_number = reports_filtered.accessionNumber.values[i].replace("-", "")
        file_name = reports_filtered.primaryDocument.values[i]

        # remove the .htm from the file name
        report_name = file_name.split(".")[0]

        # Get url using cik, access_number, and file_name
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{access_number}/{file_name}"

        # calls function to convert webpage to pdf
        convert_to_pdf(url, report_name, output_folder)


def convert_to_pdf(url, report_name, output_folder):
    """

    :param url:
    :param report_name:
    :param output_folder:
    :return:
    """
    # sets location of wkhtmltopdf.exe, change path if necessary
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    # setup config
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    try:
        # Fetch the webpage content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output PDF path
        pdf_file = os.path.join(output_folder, f"{report_name}.pdf")

        # Convert HTML to PDF
        pdfkit.from_string(html_content, pdf_file, configuration=config, options={"enable-local-file-access": ""})

        print(f"PDF successfully created at {pdf_file}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
