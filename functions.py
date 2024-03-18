"""
All the functions for the program
Enter your email in headers before running
"""

import os
import pandas as pd
import json
import requests
import pdfkit
from bs4 import BeautifulSoup
"""
# OPTIONAL: hides your email email
from my_email import hide_email
EMAIL = (hide_email.get("email"))

# required for requests
headers = {
    "User-Agent": "EMAIL",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}
"""
# enter your email prior to running
headers = {
    "User-Agent": "your_email@your_domain.com",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}


def user_input():
    """
    User selects report type (8-K, 10-k, or 10-Q) and company 'ticker'
    :return: ticker, report
    """
    while True:
        # User inputs the ticker and report type, converts to uppercase
        ticker = input("Please enter the stock ticker (ex. MSFT): ").upper()
        report = input("Please enter the report (10-K, 10-Q, 8-K): ").upper()

        # Confirm inputs are correct
        if report == "10-K":
            confirm_10k = input(f"Please confirm: \n "
                                f"You would like 10-K reports for {ticker} (Y or N): ").upper()
            if confirm_10k == "Y":
                print(f"Ok, getting 10-K annual reports for ticker {ticker}.")
                break
            else:
                print("Ok, please input your choices again:")

        elif report == "10-Q":
            confirm_10q = input(f"Please confirm: \n "
                                f"You would like  10-Q report for {ticker} (Y or N): ").upper()
            if confirm_10q == "Y":
                print(f"Ok, getting 10-Q quarterly reports for ticker {ticker}.")
                break
            else:
                print("Ok, please input your choices again:")
        elif report == "8-K":
            confirm_10q = input(f"Please confirm: \n "
                                f"You would like  8-K report for {ticker} (Y or N): ").upper()
            if confirm_10q == "Y":
                print(f"Ok, getting 8-K events reports for ticker {ticker}.")
                break
            else:
                print("Ok, please input your choices again:")
        else:
            print("You entered an invalid parameters, please re-enter your inputs:")

    return ticker, report


def ticker_to_cik(ticker):
    """
    converts ticker to CIK and gets url for dictionary of reports
    :param ticker: company ticker (str)
    :return: cik to access reports for company (str), url for all reports (str)
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
    converts dictionary to pandas df
    :param url: filings dictionary (str)
    :return: company_filings_df (pandas df)
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
    filters df based on report
    :param company_filings_df: fling in pandas (df)
    :param report: report type (10-K, 10-Q, 8-k) (str)
    :return: report_filtered pandas df with only selected report type (df)
    """
    # Sort df by 10-K
    if report == "10-K":
        report_filtered = company_filings_df[company_filings_df.form == "10-K"]
        return report_filtered

    # Sort df by 10-Q
    elif report == "10-Q":
        report_filtered = company_filings_df[company_filings_df.form == "10-Q"]
        return report_filtered

    # Sort df by 8-K reports
    elif report == "8-K":
        report_filtered = company_filings_df[company_filings_df.form == "8-K"]
        return report_filtered

    else:
        print("Invalid Report")

    return


def access_reports(report_filtered, cik, report, ticker, output_folder):
    """
    Gets the number of reports and asks user how many reports they want
    Loops through all the reports and gets url for each report requested
    10-K and 10-Q: calls convert_to_pdf
    8-K: calls  get_href_links to get ex 99.1 url (press release), calls convert_to_pdf
    :param report_filtered:
    :param cik: company CIK (str)
    :param report: report type (str)
    :param ticker: company ticker
    :param output_folder: location where pdf files will be saved
    :return:
    """
    # get the number of report_folder from the filtered df
    report_length = len(report_filtered)
    print(f"There are ({report_length}) reports\n")
    num_reports = int(input("Please enter the number of reports you want to access: "))

    # Loop through reports
    for i in range(0, num_reports):
        # Get accession number and remove the dashes
        access_number = report_filtered.accessionNumber.values[i].replace("-", "")

        # Get file name inputs
        file_name = report_filtered.primaryDocument.values[i]
        report_date = report_filtered.reportDate.values[i].replace("-", "")
        report_remove_dash = report.replace("-", "")

        # Name for pdf file: ticker + report date + report type
        report_name = ticker + '_' + report_date + '_' + report_remove_dash

        # Get url using cik, access_number, and file_name
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{access_number}/{file_name}"

        # Create pdf from the 10-K and 10-Q html link
        if report == "10-K" or report == "10-Q":
            print(f"**** Report {i + 1} ****")
            # calls function to convert webpage to pdf
            convert_to_pdf(url, report_name, output_folder)

        # Get the exhibit 99.1 file link
        elif report == "8-K":
            print(f"**** Report {i + 1} ****")
            exhibit_link = get_href_links(url)

            # Check if ex 99.1 report exists (check if empty list)
            if not exhibit_link:
                print("no ex 99.1 in this report")
                print("\n")
            else:
                convert_to_pdf(exhibit_link, report_name, output_folder)

        else:
            print("Invalid Report")
    return


def get_href_links(url):
    """
    Get hyperlink url for ex 99.1 file and calls convert_to_pdf
    :param url: ex 99.1 link (str)
    :return: None
    """
    # Scrape webpage
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')

    # split at last / from url
    base_url = url.rsplit('/', maxsplit=1)[0] + '/'
    print(f"Base URL: {base_url}")

    # remove duplicates
    out = set()

    # look for exhibit 99.1 by searching for "ex99"
    for link in soup.select('[href*="ex99"]'):

        # add extension to base url
        out.add(base_url + link['href'])

    # check if there is an ex 99.1 file hyperlink
    out_list = list(out)
    if not out_list:
        return out_list
    else:
        return out_list[0]


def convert_to_pdf(url, report_name, output_folder):
    """
    Coverts html webpage to a pdf file and saves file to output folder
    :param url: webpage to convert to pdf (str)
    :param report_name: name of report ticker-date-report (str)
    :param output_folder: desired folder to save report (str)
    :return: None
    """
    # sets location of wkhtmltopdf.exe, change path if necessary
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    # setup configs
    configs = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

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
        pdfkit.from_string(html_content, pdf_file, configuration=configs, options={"enable-local-file-access": ""})

        # Confirm pdf created
        print(f"PDF file {pdf_file} successfully created!")
        print("\n")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

    return
