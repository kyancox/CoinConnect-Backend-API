from cb import coinbase
from gemini import gemini
from ledger import ledger
import pandas as pd
import pprint
from collections import defaultdict
from cmc import loadNames, getPrices
from portfolioClass import MasterPortfolio


accounts = [coinbase, gemini, ledger]

master = MasterPortfolio(accounts)

master.showAssets()