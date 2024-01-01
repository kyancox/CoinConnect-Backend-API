from cmc import getPrices

class Portfolio:

    exchange = ""
    portfolio = {}
    prices = []

    def __init__(self, exchange, portfolio):
        self.exchange = exchange
        self.portfolio = portfolio

    # Clean assets so that accounts with no amount of cryptocurrency (0) are removed
    def cleanAssets(self):
        # print(f"Before: {len(accounts)}\n")
        # pprint.pprint(accounts)
        clean_accounts = {}

        for key, value in self.portfolio.items():
            if float(value[1]) != 0:
                clean_accounts[key] = value

        # print(f"After: {len(clean_accounts)}\n")
        # pprint.pprint(clean_accounts)
                
        self.portfolio = clean_accounts

    # Loads real-time prices of coins into given portfolio
    def loadPrices(self):

        self.prices = getPrices(self.portfolio)

        i = 0
        for key, value in self.portfolio.items():
            value.append(self.prices[i])
            i += 1

    # Loads current balance of coins into given portfolio using real-time prices
    def loadBalance(self):
        for key, value in self.portfolio.items():
            #string = "$"
            #string += str(float(value[1]) * float(value[2]))
            value[2] = str(float(value[1]) * float(value[2]))

        self.loadPrices()


    # Calculates total balance of given portfolio
    def totalBalance(self):
        return "$" + str(sum([float(value[2]) for key, value in self.portfolio.items()])) + " USD"

    # Prints assets and all details of portfolio into terminal 
    def showAssets(self):

        # clean_accounts = cleanAssets(accounts)
        # prices = getPrices(clean_accounts)
        # accounts = loadPrices(clean_accounts, prices)
        # portfolio = loadBalance(accounts, prices)

        self.cleanAssets()
        self.loadPrices()
        self.loadBalance()

        print(f"\nShowing assets in {self.exchange} exchange:\n")

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
        print(f"Total Balance: {self.totalBalance()}\n")