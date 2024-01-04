import pandas as pd
from portfolioClass import Portfolio
from ledger_sec import filePath

df = pd.read_csv(filePath)
df_filtered = df[df['Operation Type'].isin(['IN', 'OUT'])].copy(deep=True)

df_filtered['Adjusted Amount'] = df_filtered.apply(
    lambda row: row['Operation Amount'] if row['Operation Type'] == 'IN' else -row['Operation Amount'], 
    axis = 1
)

ledgerAssets = df_filtered.groupby('Currency Ticker')['Adjusted Amount'].sum().to_dict()

ledger = Portfolio("Ledger", ledgerAssets)

if __name__ == "__main__":
    ledger.showAssets()