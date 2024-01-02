from cb import coinbase
from gemini import gemini
from ledger import ledger
import pandas as pd

'''
Would like to make a file that contains all three accounts 

We can make an array of accounts?
'''

accounts = [coinbase, gemini, ledger]

'''
I think we are making a new class, called masterPortfolio()
'''

def masterPortfolio(Portfolio):
    
    accounts = []
    numAccounts = 0

    def __init__(self, accounts):
        self.accounts = accounts
        numAccounts = len(accounts)

        '''
        With this, we can use inheritance to get the methods from Portfolio()
        - we also want cmc methods to getPrices and loadNames 
        '''