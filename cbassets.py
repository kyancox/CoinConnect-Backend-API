from coinbase.wallet.client import Client
from cb_sec import api_key, api_secret
from cmc import getPrices
import pprint

# Coinbase API V2

client = Client(api_key, api_secret)

accounts = client.get_accounts(limit='100')
# https://stackoverflow.com/questions/67343099/coinbase-api-btc-account-missing
# https://forums.coinbasecloud.dev/t/client-get-accounts-only-gives-certain-cryptos-for-output/890/4

data = accounts.data

accounts = {key.balance.currency:[key.currency.name, key.balance.amount] for key in data}

# Clean assets so that accounts with no amount of cryptocurrency (0) are removed
def cleanAssets(portfolio):
    # print(f"Before: {len(accounts)}\n")
    # pprint.pprint(accounts)
    clean_accounts = {}

    for key, value in portfolio.items():
        if float(value[1]) != 0:
            clean_accounts[key] = value

    # print(f"After: {len(clean_accounts)}\n")
    # pprint.pprint(clean_accounts)
            
    return clean_accounts

# Loads real-time prices of coins into given portfolio
def loadPrices(portfolio, prices):
    i = 0
    for key, value in portfolio.items():
        value.append(prices[i])
        i += 1

    return portfolio

# Loads current balance of coins into given portfolio using real-time prices
def loadBalance(portfolio, prices):
    for key, value in portfolio.items():
        #string = "$"
        #string += str(float(value[1]) * float(value[2]))
        value[2] = str(float(value[1]) * float(value[2]))

    portfolio = loadPrices(portfolio, prices)
    return portfolio

# Calculates total balance of given portfolio
def totalBalance(portfolio):
    return "$" + str(sum([float(value[2]) for key, value in portfolio.items()])) + " USD"

# Prints assets and all details of portfolio into terminal 
def showAssets(accounts):

    clean_accounts = cleanAssets(accounts)
    prices = getPrices(clean_accounts)
    accounts = loadPrices(clean_accounts, prices)
    portfolio = loadBalance(accounts, prices)

    # Symbol | Name | Amount | Balance | Real-Time Price
    header = f"{'Symbol':<5} | {'Name':<25} | {'Amount':<12} | {'Balance':<11} | {'Real-Time Price':<15}"
    print(header)
    print('-'*90)
    for key, value in portfolio.items():
        symbol = key
        name = value[0]
        amount = round(float(value[1]), 5)
        balance = round(float(value[2]), 4)
        price = round(float(value[3]), 4)
        print(f"{symbol:<6} | {name:<25} | {amount:<12} | ${balance:<10} | ${price:<10}")
    print()
    print(f"Total Balance: {totalBalance(portfolio)}\n")

if __name__ == '__main__':
    # clean_accounts = cleanAssets(accounts)
    # prices = getPrices(clean_accounts)
    # accounts = loadPrices(clean_accounts, prices)
    # accounts = loadBalance(accounts, prices)

    showAssets(accounts)
