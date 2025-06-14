# Wealthsimple Inbox Reader

This script parses email exports to generate a complete summary of your Wealthsimple account activity.

## Overview

- **Input:**  
  An `mbox` file exported via Google Takeout containing your Wealthsimple emails.

- **Output:**  
  - `JSON` file with structured transaction data.
  - `CSV` file for easy import into spreadsheets or analysis tools.
    
## Supporting Files

- **`missing_transactions.json`**  
  Manually add transactions that are missing from your email exports or were not emailed.
  ```json
      {
        "Type": "Stock Reorganization",
        "Account": "TFSA",
        "Amount": "4",
        "Symbol": "NVDA.NE",
        "Date": "2024-07-10T10:07:50.000Z",
        "Shares": "0",
        "Avg Price": "0",
        "Action": "SPLIT"
    }
- **`ticker_mapping.json`**  
  Remap tickers as needed.  
  Example:
  ```json
  {
    "TD": "TD.TO"
  }
