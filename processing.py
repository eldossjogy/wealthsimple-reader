import os
from datetime import datetime, timezone, timedelta
import re
import json
import csv
import shutil

# Load the mapping
with open("ticker_mapping.json", "r") as f:
    ticker_mapping = json.load(f)

with open("missing_transactions.json", "r") as f:
    missing_transaction = json.load(f)

# Pattern for purchase
patterns = {
    "account": r"Account:\s*\*?(.*?)\*?\s*(?:$|\n)",
    "type": r"Type:\s*(.*?)\s*(?:$|\n)",  # allow any spaces or newline
    "symbol": r"Symbol:\s*\*?(\w+)\*?",
    "shares": r"Shares:\s*\*?(.*?)\*?\s*(?:$|\n)",
    "average_price": r"Average price:\s*\*?\$?(.*?)\*?\s*(?:$|\n)",
    "total_cost": r"Total cost:\s*\*?\$?(.*?)\*?\s*(?:$|\n)",
    "time": r"Time:\s*\*?(.*?)\*?\s*(?:$|\n)",
    "amount": r"Amount:\s*-?\s*C?\$?\s*(\d+\.\d+)",
    "subject": r"Subject:\s*(.*)",
    "date": r"Date:\s*(.*)",
    "total_value": r"Total value:\s*\*?\$?(.*?)\*?\s*(?:$|\n)",
}

dividends = {
    "You earned a dividend",
    "You have earned a dividend",
    "You have received a dividend",
    "You got a dividend!",
}

purchase = {
    "Your order has been filled",
}

deposits = {
    "You made a deposit",
    "Your deposit is complete!",
}

output_dir = "./emails"
ignore_dir = "./ignored_emails"
all_data = []


def cleanup(directory):
	if os.path.exists(directory):
			shutil.rmtree(directory)
	print("Cleanup directory")
	

def convert_to_est_iso8601(date_str: str) -> str:
    date_str = re.sub(r"\s*\(.*?\)", "", date_str).strip()
    dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    est_offset = timedelta(hours=-5)
    est_tz = timezone(est_offset)
    dt_est = dt.astimezone(est_tz)
    iso_format = dt_est.strftime("%Y-%m-%dT%H:%M:%S.000-05:00")
    return iso_format


for filename in os.listdir(output_dir):
    f = os.path.join(output_dir, filename)
    if os.path.isfile(f):
        with open(f, "r", encoding="utf-8") as file_each:
            text = file_each.read()
            data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                data[key] = match.group(1).strip() if match else None

            # Variable Formatting
            if data["total_cost"]:
                data["total_cost"] = data["total_cost"].replace(",", "")

            data["date"] = convert_to_est_iso8601(data["date"])
            

            # Adding Variable 
            data["file_id"] = filename

            # Adding "Action" Variable
            if data["type"] and "Buy" in data["type"]:
                data["Action"] = "BUY"
                data["type"] = data["type"].replace("*","").replace("Buy","").strip()
                
            if data["type"] and "Sell" in data["type"]:
                data["Action"] = "SELL"
                data["type"] = data["type"].replace("*","").replace("Sell","").strip()

            # Updating "subject" variable
            if data["subject"] in dividends:
                data["Action"] = "DIVIDEND"
                data["subject"] = "Dividend"
            elif data["subject"] in purchase:
                data["subject"] = "Purchase"
            elif data["subject"] in deposits:
                data["subject"] = "Deposit"
                data["Action"] = "DEPOSIT"

            # Updating Ticker Symbols
            symbol = data.get("symbol")
            if symbol in ticker_mapping:
                data["symbol"] = ticker_mapping[symbol]

            all_data.append(data)


all_data_sorted = sorted(all_data, key=lambda x: x["date"], reverse=True)


# Write parsed data to JSON
# with open("parsed_output.json", "w", encoding="utf-8") as f:
#     json.dump(all_data_sorted, f, indent=4)

# Add Missing Transactions
formatted_output = []
for transaction in all_data_sorted:
    if transaction.get('Action') == "BUY":
        temp_formatted_transaction = {}
        temp_formatted_transaction["Type"] = transaction.get("type")    
        temp_formatted_transaction["Account"] = transaction.get("account")    
        temp_formatted_transaction["Amount"] = transaction.get("total_cost")    
        temp_formatted_transaction["Symbol"] = transaction.get("symbol")    
        temp_formatted_transaction["Date"] = transaction.get("date")    
        temp_formatted_transaction["Shares"] = transaction.get("shares")    
        temp_formatted_transaction["Avg Price"] = transaction.get("average_price")    
        temp_formatted_transaction["Action"] = transaction.get("Action")         
        if any(value is None for value in temp_formatted_transaction.values()):
            print("\033[91mSome \033[1mBUY\033[0;91m transaction contains None:\033[0m")
            print(transaction)
            break
        formatted_output.append(temp_formatted_transaction)
    elif transaction.get('Action') == "SELL":
        temp_formatted_transaction = {}
        temp_formatted_transaction["Type"] = transaction.get("type")    
        temp_formatted_transaction["Account"] = transaction.get("account")    
        temp_formatted_transaction["Amount"] = transaction.get("total_value")    
        temp_formatted_transaction["Symbol"] = transaction.get("symbol")    
        temp_formatted_transaction["Date"] = transaction.get("date")    
        temp_formatted_transaction["Shares"] = transaction.get("shares")    
        temp_formatted_transaction["Avg Price"] = transaction.get("average_price")    
        temp_formatted_transaction["Action"] = transaction.get("Action") 
        if any(value is None for value in temp_formatted_transaction.values()):
            print("\033[91mSome \033[1mSELL\033[0;91m transaction contains None:\033[0m")
            print(transaction)
            break
        formatted_output.append(temp_formatted_transaction)
    elif transaction.get('Action') == "DIVIDEND":
        temp_formatted_transaction = {}
        temp_formatted_transaction["Type"] = "Dividends"    
        temp_formatted_transaction["Account"] = transaction.get("account")    
        temp_formatted_transaction["Amount"] = transaction.get("amount")    
        temp_formatted_transaction["Symbol"] = transaction.get("symbol")    
        temp_formatted_transaction["Date"] = transaction.get("date")    
        temp_formatted_transaction["Shares"] = ''  
        temp_formatted_transaction["Avg Price"] = "TBD"    
        temp_formatted_transaction["Action"] = transaction.get("Action") 
        if any(value is None for value in temp_formatted_transaction.values()):
            print("\033[91mSome \033[1mDIVIDEND\033[0;91m transaction contains None:\033[0m")
            print(temp_formatted_transaction)
            print(transaction.get("file_id"))
            print(transaction)
            break    
        formatted_output.append(temp_formatted_transaction)
    elif transaction.get('Action') == "DEPOSIT":
        temp_formatted_transaction = {}
        temp_formatted_transaction["Type"] = "Deposit"    
        temp_formatted_transaction["Account"] = transaction.get("account")    
        temp_formatted_transaction["Amount"] = transaction.get("amount")    
        temp_formatted_transaction["Symbol"] = "$CASH-CAD"   
        temp_formatted_transaction["Date"] = transaction.get("date")    
        temp_formatted_transaction["Shares"] = ''  
        temp_formatted_transaction["Avg Price"] = 1
        temp_formatted_transaction["Action"] = transaction.get("Action") 
        if any(value is None for value in temp_formatted_transaction.values()):
            print("\033[91mSome \033[1mDEPOSIT\033[0;91m transaction contains None:\033[0m")
            print(temp_formatted_transaction)
            break   
        formatted_output.append(temp_formatted_transaction)
    else:
        print("Something wrong")
        print(transaction)
        break;



formatted_output.extend(missing_transaction)

# # for every dividednce find its closes dividence revinvest or fractional buying of the same symbol and copy its avg amount
transcations = sorted(formatted_output, key=lambda x: datetime.fromisoformat(x["Date"]), reverse=True)

for t_dic in transcations:
	if t_dic.get("Type") == "Dividends":
		ticker = t_dic.get("Symbol")
		for n_t_dic in transcations[transcations.index(t_dic):]:
			if n_t_dic.get("Symbol") == ticker and n_t_dic.get("Type") != "Dividends":
				t_dic["Avg Price"] = n_t_dic.get("Avg Price")
				break


formatted_output = sorted(transcations, key=lambda x: datetime.fromisoformat(x["Date"]), reverse=True)
# formatted_output.append(missing_transaction)

# Write sorted data to JSON
with open("formatted_out.json", "w", encoding="utf-8") as f:
    json.dump(formatted_output, f, indent=4)

# print("Done extracting")

# Dumps dictionary to csv used in wealthfolio
with open("data.csv", mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=formatted_output[0].keys())
    writer.writeheader()
    writer.writerows(formatted_output)

print(f"Data has been written to data.csv")

# if debug == false:
cleanup(output_dir)
cleanup(ignore_dir)