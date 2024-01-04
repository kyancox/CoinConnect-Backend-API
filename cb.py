from coinbase.wallet.client import Client
from cb_sec import api_key, api_secret
import pprint
from portfolioClass import Portfolio

# Coinbase API V2

client = Client(api_key, api_secret)

accounts = client.get_accounts(limit='100')
# https://stackoverflow.com/questions/67343099/coinbase-api-btc-account-missing
# https://forums.coinbasecloud.dev/t/client-get-accounts-only-gives-certain-cryptos-for-output/890/4

data = accounts.data

accounts = {key.balance.currency:[key.currency.name, key.balance.amount] for key in data}

accounts2 = {key.balance.currency:key.balance.amount for key in data}

coinbase = Portfolio("Coinbase", accounts)

if __name__ == '__main__':
    pprint.pprint(accounts2)
    #coinbase.showAssets()


