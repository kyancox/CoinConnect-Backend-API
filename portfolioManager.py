
from flask import abort, jsonify
from portfolioClass import MasterPortfolio
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
from io import BytesIO

# Import for Coinbase
from cb import coinbasePortfolio
# Import for Gemini
from gemini import geminiPortfolio
# Import for Ledger
from ledger import ledgerPortfolio

class PortfolioManager:
    def __init__(self):
        self.coinbase = None
        self.gemini = None
        self.ledger = None
        self.master = None
        self.accounts = []

    def initCoinbase(self, key, secret):

        if self.coinbase in self.accounts:
            self.accounts.remove(self.coinbase)

        try:
            self.coinbase = coinbasePortfolio(key, secret)
            print('Coinbase portfolio initialized successfully')
        except RequestsJSONDecodeError:
            #return jsonify({'message':'api_key or api_secret for Coinbase was invalid.'}), 404
            abort(404, 'api_key or api_secret for Coinbase was invalid.')
        
        self.accounts.append(self.coinbase)
        print("coinbase account appended to accounts")

    def initGemini(self, key, secret):

        if self.gemini in self.accounts:
            self.accounts.remove(self.gemini)

        try:
            self.gemini = geminiPortfolio(key, secret)
            print('Gemini portfolio initialized successfully')
        except Exception:
            #return jsonify({'message':'api_key or api_secret for Gemini was invalid.'}), 404
            abort(404, 'api_key or api_secret for Gemini was invalid.')
        
        self.accounts.append(self.gemini)
        print("gemini account appended to accounts")

    def initLedger(self, data):
        file_data = data

        # file_data must be a BytesIO() object 
        if type(file_data) != BytesIO:
            file_data = BytesIO(data)

        if self.ledger in self.accounts:
            self.accounts.remove(self.ledger)

        try:
            self.ledger = ledgerPortfolio(file_data)
            print('Ledger portfolio initialized successfully')
        except Exception as e:
            print(e)
            abort(404, 'CSV file for Ledger was invalid.')
        
        self.accounts.append(self.ledger)
        print("ledger account appended to accounts")

    def initMaster(self):
        if len(self.accounts) == 0:
            return jsonify({'message':'Accounts are invalid...'}), 404

        self.master = MasterPortfolio(self.accounts)