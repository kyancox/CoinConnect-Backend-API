import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import base64
import hmac
import hashlib
import datetime, time
import pprint

from portfolioClass import Portfolio

def geminiPortfolio(api_key, api_secret):
    url = "https://api.gemini.com/v1/balances"

    api_secret = api_secret.encode()

    t = datetime.datetime.now()
    payload_nonce = time.time()
    payload =  {"request": "/v1/balances", "nonce": payload_nonce}
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(api_secret, b64, hashlib.sha384).hexdigest()

    request_headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': b64,
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
        }

    balances = []

    try:
        response = requests.post(url, headers=request_headers)
        balances = response.json() # returns a list of dictionaries

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        raise e

    balances = {balances[i]['currency']:balances[i]['amount'] for i in range(1, len(balances))}

    return Portfolio("Gemini", balances)

