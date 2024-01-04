from cb import coinbase
from gemini import gemini
from ledger import ledger
import pandas as pd
import pprint
from collections import defaultdict
from cmc import loadNames, getPrices
from portfolioClass import MasterPortfolio


accounts = [coinbase, gemini, ledger]

# class MasterPortfolio():
    
#     accounts = []
#     numAccounts = 0
#     exchangeData = {}
#     balances = {}
#     portfolio = {}


#     def __init__(self, accounts):
#         self.accounts = accounts
#         self.numAccounts = len(accounts)
#         self.exchangeCount = defaultdict(list)
#         self.balances = defaultdict(float)


#     def setExchangeData(self):
#         for account in self.accounts:
#             portfolio = account.getPortfolio()
#             exchange = account.getExchange()
#             for coin in portfolio:
#                 self.exchangeCount[coin].append(exchange)
            
#     def getExchangeData(self):
#         return self.exchangeCount
    
#     def setBalances(self):
#         for account in self.accounts:
#             portfolio = account.getPortfolio()
#             for coin in portfolio:
#                 self.balances[coin] += float(portfolio[coin][1])

#     def removeZero(self):
#         new = {}
#         for asset, value in self.balances.items():
#             if value != 0:
#                 new[asset] = value
#         self.balances = new

#     # Loads real-time prices of coins into given portfolio
#     def loadPrices(self):

#         prices = getPrices(self.portfolio)

#         i = 0
#         for key, value in self.balances.items():
#             value.append(prices[i])
#             i += 1

#     # Loads current balance of coins into given portfolio using real-time prices
#     def loadBalance(self):
#         for key, value in self.portfolio.items():
#             value[2] = str(float(value[1]) * float(value[2]))

#         self.loadPrices()

#     def loadData(self):
#         self.setExchangeData()
#         self.setBalances()
#         self.removeZero()
#         self.portfolio = loadNames(self.balances)
#         self.loadPrices()
#         self.loadBalance()

#     def showAssets(self):
#         pass




master = MasterPortfolio(accounts)


master.loadData()
pprint.pprint(master.portfolio)

pprint.pprint(master.getExchangeData())
