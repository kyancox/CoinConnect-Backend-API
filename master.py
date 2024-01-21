from cb_sec import coinbase
from gemini_sec import gemini
from ledger_sec import ledger
from portfolioClass import MasterPortfolio
import pprint

accounts = [coinbase, gemini, ledger]
master = MasterPortfolio(accounts)

if __name__ == "__main__":    
    
    master.showAssets()
