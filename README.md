# 10-K and 10-Q Reports from SEC Database (EDGAR) 

- SEC Main Page: https://www.sec.gov/
- SEC Developer Resources: https://www.sec.gov/developer

## Overview
The program gets 10-K or 10-Q reports from the SEC database for a selected stock and saves them as a pdf file.  
The user has the option to select the number of reports for a selected stock.  The program is limited to 10-K 
and 10-Q reports.

## Terms
* 10-K: Annual shareholder report
* 10-Q: Quarterly shareholder report
* CIK: Central Index Key-EDGAR uses this number to identify a Company 
* Ticker: ticker of a stock (example: Microsoft ticker is MSFT)

## Requirements Library
* pandas
* json
* os
* requests
* pdfkit
* __requires your email address in the headers setup for requests.__  Add your email address prior to running.

```
headers = {
    "User-Agent": "your_email@your_domain.com",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}
```  
* (optional) hide your email:
- create a .env file with MY_EMAIL=your_email@my_domain.com
- add .env file to.gotignore
- Include the following:
```
from decouple import config
EMAIL = config("MY_EMAIL")

headers = {
    "User-Agent": "EMAIL",  # Your email as the User-Agent
    "Accept-Encoding": "gzip, deflate"
}

```

## Notes on pdfkit
* requires _wkhtmltopdf_ to be installed 
* This is a setup for a Windows environment, not sure if it works in other operating systems.
```
path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" # is the path to the executable
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)' # sets configuration
pdfkit.from_string(html_content, pdf_file, configuration=config, options={"enable-local-file-access": ""}) 
```

## Functions Overview
1) User Input Setup: enter stock ticker, desired report, and number of reports
    function: user_inputs
    * Input parameters (by user):
        - Input a ticker (example AMZN)
        - Report Type (10-K or 10-Q)
        - Enter number of reports 
    * Outputs:
        - Ticker
        - Report type
        - Number of reports

2) Get CIK for ticker and generate url for report filings
    * function: ticker_to_cik
    * input: ticker
    * output: url for report filings

3) Convert filings dictionary to pandas
    * function: filings_to_df
    * Input: url
    * Output: company_filings_df

4) Filter df report for either 10-K or 10-Q
    * function: filter_reports
    * Input: company_filings_df
    * output: reports_filtered

5) Iterate through links and create pdf file of report
    * functions: access_reports, webpage_to_pdf
    * Inputs: reports_filtered, num_reports, cik, output_folder
    * Outputs: pdf file saved to reports_folder.  File format *ticker-report date.pdf*

#### Notes
* Program can be modified to include other reports like 8-K