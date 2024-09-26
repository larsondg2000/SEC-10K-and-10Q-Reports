"""
Program to get 10-K, 10-Q, 8-K reports from SEC database (EDGAR).
    * 10-K: Annual shareholder report
    * 10-Q Quarterly shareholder report
    * 8-K: SEC Form 8-K is a report that companies must file with the Securities and Exchange Commission (SEC) to
        announce major events that shareholders should know about.  It includes press release exhibits.
    * SEC Exhibit 99.1: a document that is filed with the Securities and Exchange Commission (SEC) by companies to
        provide additional information about a particular event or transaction
    * Companies identified by Central Index Key (CIK)
"""
from functions import user_input, ticker_to_cik, filings_to_df, filter_reports, access_reports


def main():
    """

    :return:
    """
    # pdf save location: change to desired location
    # Default is root directory in report_folder
    output_folder = r"C:\Users\17272\OneDrive\Desktop\Investing\CRWD"

    # User enters company ticker and report type
    ticker, report = user_input()

    # Gets CIK for ticker and all the filings for that ticker
    cik, url = ticker_to_cik(ticker)

    # Converts filings to pandas
    company_filings_df = filings_to_df(url)

    # Filter df by report
    report_filtered = filter_reports(company_filings_df, report)

    # Get urls and create pdf file
    access_reports(report_filtered, cik, report, ticker, output_folder)


if __name__ == "__main__":
    main()
