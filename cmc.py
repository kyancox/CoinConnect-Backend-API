from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from cmc_sec import api_key
import json
import pprint

# CoinMarketCap API to get real-time prices

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


def getPrices(dictionary):

    keys = list(dictionary.keys())
    symbolString = ','.join(keys) # String of comma-separated symbols for parameter call

    parameters = {
        'symbol': symbolString,
        'convert':'USD',
        'skip_invalid':'true'
    }

    headers = {
        'Accepts':'application/json',
        'X-CMC_PRO_API_KEY':api_key
    }

    prices = []

    # Initialize Session
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        data = data['data']

        for i in range(len(keys)):
            coinPrice = data[keys[i]][0]['quote']['USD']['price']
            prices.append(coinPrice)
        
    except(ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return prices
