from cmc import getPrices, loadNames 

class Portfolio:

    def __init__(self, account, portfolio):
        self.account = account
        self.portfolio = portfolio # Write error if portfolio is not in {'string':float} form 
        self.dataLoaded = False

    # Requires loadData() to be called. 
    def sortPortfolio(self):
        if not self.dataLoaded: raise Exception("Data is not loaded.")

        sortedPortfolio = sorted(self.portfolio.items(), key = lambda coin: float(coin[1][2]), reverse = True)
        sortedPortfolio = dict(sortedPortfolio)
        
        self.portfolio = sortedPortfolio


    # Clean assets so that accounts with no amount of cryptocurrency (0) are removed
    def cleanAssets(self):
        clean_accounts = {}

        for key, value in self.portfolio.items():
            if float(value[1]) != 0:
                clean_accounts[key] = value
                
        self.portfolio = clean_accounts

        new = {}
        for asset, value in self.balances.items():
            if value != 0:
                new[asset] = value
        self.balances = new

    # Loads real-time prices of coins into given portfolio
    def loadPrices(self):

        prices = getPrices(self.portfolio)

        i = 0
        for key, value in self.portfolio.items():
            value.append(prices[i])
            i += 1

    # Loads current balance of coins into given portfolio using real-time prices
    def loadBalance(self):
        for key, value in self.portfolio.items():
            value[2] = str(float(value[1]) * float(value[2]))

        self.loadPrices()


    # Calculates total balance of given portfolio
    def totalBalance(self):
        return "$" + str(sum([float(value[2]) for key, value in self.portfolio.items()])) + " USD"

    def loadData(self):
        
        self.cleanAssets()
        self.loadPrices()
        self.loadBalance()
        self.dataLoaded = True

    # Prints assets and all details of portfolio into terminal 
    def showAssets(self):

        if not self.dataLoaded: self.loadData()
        self.sortPortfolio()

        print("\nShowing your assets in " + "\033[4m" + self.account + "\033[0m" + ":\n")

        # Symbol | Name | Amount | Balance | Real-Time Price
        header = f"{'Symbol':<5} | {'Name':<25} | {'Amount':<12} | {'Balance':<11} | {'Real-Time Price':<15}"
        print(header)
        print('-'*90)
        for key, value in self.portfolio.items():
            symbol = key
            name = value[0]
            amount = round(float(value[1]), 5)
            balance = round(float(value[2]), 4)
            price = round(float(value[3]), 4)
            print(f"{symbol:<6} | {name:<25} | {amount:<12} | ${balance:<10} | ${price:<10}")
        print()
        print("Total Balance in " + '\033[4m' + self.account + "\033[0m" + ": " + self.totalBalance() + "\n")

    def getPortfolio(self):
        return self.portfolio
    
    def getExchange(self):
        return self.account
    
    def getPrices(self):
        return getPrices(self.portfolio)
    
    

from collections import defaultdict

class MasterPortfolio(Portfolio):
    
    accounts = []
    numAccounts = 0
    exchangeData = {}
    balances = {}
    portfolio = {}


    def __init__(self, accounts):
        self.accounts = accounts
        self.numAccounts = len(accounts)
        self.exchangeCount = defaultdict(list)
        self.balances = defaultdict(float)

        super.__init__("Master", self.portfolio)


    def setExchangeData(self):
        for account in self.accounts:
            portfolio = account.getPortfolio()
            exchange = account.getExchange()
            for coin in portfolio:
                self.exchangeCount[coin].append(exchange)
            
    def getExchangeData(self):
        return self.exchangeCount
    
    def setBalances(self):
        for account in self.accounts:
            portfolio = account.getPortfolio()
            for coin in portfolio:
                self.balances[coin] += float(portfolio[coin][1])

    def removeZeros(self):
        new = {}
        for asset, value in self.balances.items():
            if value != 0:
                new[asset] = value
        self.balances = new

    # Loads real-time prices of coins into given portfolio
    def loadPrices(self):

        prices = getPrices(self.portfolio)

        i = 0
        for key, value in self.balances.items():
            value.append(prices[i])
            i += 1

    # Loads current balance of coins into given portfolio using real-time prices
    def loadBalance(self):
        for key, value in self.portfolio.items():
            value[2] = str(float(value[1]) * float(value[2]))

        self.loadPrices()

    def initPortfolio(self):
        pass

    def loadData(self):
        self.setExchangeData()
        self.setBalances()
        self.removeZeros()
        self.portfolio = loadNames(self.balances)
        self.loadPrices()
        self.loadBalance()

    def showAssets(self):
        pass
