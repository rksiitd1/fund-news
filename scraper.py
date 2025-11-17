import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://inc42.com/buzz/from-finnable-to-bombay-shaving-company-indian-startups-raised-163-mn-this-week/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all tables
tables = pd.read_html(response.text)

# Print all tables to identify correct one
for i, table in enumerate(tables):
    print(f"Table {i}:")
    print(table.head())
    print("\n" + "="*50 + "\n")

# If you know the index of the desired table, for example 0:
funding_table = tables[0]
funding_table.to_csv("funding_table.csv", index=False)
print("Funding table saved to funding_table.csv")
