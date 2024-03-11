"""
Program to get 10-K and 10-Q reports from SEC database (EDGAR).
10-K Annual shareholder report
10-Q Quarterly shareholder report
Companies identified by Central Index Key (CIK)
Steps:
1) Setup
    function: user_inputs
    Input parameters (by user):
        Input a ticker (example AMZN)
        Report Type (10-K or 10-Q)
        Enter number of reports (set default to 5 years and 20 quarters)
    Outputs:
        Ticker
        Report
        Years
1a) Get JSON file for company, tickers, CIK, and exchange and save to root directory

2) Get CIK for ticker and generate url for report filings
    function: ticker_to_cik
    input: Ticker
    output: url for report filings

3) Convert filings dictionary to pandas
    function: filings_to_df
    Input: url
    Output: company_filings_df

4) Filter df report for either 10-K or 10-Q
    function: filter_reports
    Input: company_filings_df
    output: reports_filtered

5) Iterate through links and create pdf file of report
    functions: access_reports, webpage_to_pdf
    Inputs: reports_filtered, num_reports, cik, output_folder
    Outputs: pdf file
"""
from functions import download_json, user_input, ticker_to_cik, filings_to_df, filter_reports, access_reports


def main():
    """
    :return:
    """
    # Set defaults
    output_folder = "report_folder"

    # Run this once to get json file
    # download_json()
    ticker, report, num_reports = user_input()
    cik, url = ticker_to_cik(ticker)
    company_filings_df = filings_to_df(url)
    report_filtered = filter_reports(company_filings_df, report)
    access_reports(report_filtered, num_reports, cik, output_folder)


if __name__ == "__main__":
    main()
