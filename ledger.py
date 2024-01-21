import pandas as pd
from portfolioClass import Portfolio

def ledgerPortfolio(file_data):

    df = pd.read_csv(file_data)

    df_filtered = df[df['Operation Type'].isin(['IN', 'OUT'])].copy(deep=True)

    df_filtered['Adjusted Amount'] = df_filtered.apply(
        lambda row: row['Operation Amount'] if row['Operation Type'] == 'IN' else -row['Operation Amount'], 
        axis = 1
    )

    ledgerAssets = df_filtered.groupby('Currency Ticker')['Adjusted Amount'].sum().to_dict()

    return Portfolio("Ledger", ledgerAssets)
