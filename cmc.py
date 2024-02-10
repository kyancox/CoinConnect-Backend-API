from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint

# CoinMarketCap API to get real-time prices

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
api_key = '9b27d22e-db5b-4878-85d1-39814c5fdccd'

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
            print(f'getPrices iteration: {str(i)}')
            coinPrice = ""
            try:
                coinPrice = data[keys[i]][0]['quote']['USD']['price']
            except Exception:
                coinPrice = "0"
            prices.append(coinPrice)
        
    except(ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return prices

# for Gemini
def loadNames(dictionary):

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

    # Initialize Session
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        data = data['data']

        for i in range(len(keys)):
            # IF NAME NOT FOUND, PUT A 'FILLER' NAME THAT SAYS 'NAME NOT FOUND' or '0'
            print(f'loadNames iteration: {str(i)}')
            symbol = keys[i]
            name = ""
            try:
                name = data[symbol][0]['name']
            except Exception:
                name = "Name Not Found"
            #coinPrice = data[keys[i]][0]['quote']['USD']['price']
            dictionary[symbol] = [name, dictionary[symbol]]
        
    except(ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    


