from cb import coinbase
from gemini import gemini
from ledger import ledger
from portfolioClass import MasterPortfolio
import pprint

accounts = [coinbase, gemini, ledger]
master = MasterPortfolio(accounts)

if __name__ == "__main__":

    master.pandasToExcel()
    #master.showAssets()



    # df = master.portfolioToDataframe()
    # for value in df.values():
    #     print(len(value))


    # master.generateBalances()

    # print(len(master.balances))