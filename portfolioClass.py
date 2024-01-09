from datetime import datetime
import cmc as cmc

class Portfolio:

    def __init__(self, accountName, portfolio):
        self.accountName = accountName
        if type(portfolio) != dict: raise TypeError()
        self.portfolio = {key:float(value) for key, value in portfolio.items()}
        self.dataLoaded = False

    # Clean assets so that accounts with no amount of cryptocurrency (0) are removed
    def cleanAssets(self):
        new = {}

        for asset, value in self.portfolio.items():
            if value != 0:
                new[asset] = value

        self.portfolio = new

    #
    def loadNames(self):
        cmc.loadNames(self.portfolio)

    # Loads real-time prices of coins into given portfolio
    def loadPrices(self):
        prices = cmc.getPrices(self.portfolio)

        i = 0
        for key, value in self.portfolio.items():
            value.append(prices[i])
            i += 1

    # Loads current balance of coins into given portfolio using real-time prices
    def loadBalance(self):
        for key, value in self.portfolio.items():
            value[2] = float(value[1]) * float(value[2])

        self.loadPrices()


    # Calculates total balance of given portfolio
    def totalBalance(self):
        return "$" + str(sum([float(value[2]) for key, value in self.portfolio.items()])) + " USD"

    def loadData(self):
        if self.dataLoaded: return

        self.cleanAssets()
        self.loadNames()
        self.loadPrices()
        self.loadBalance()
        self.sortPortfolio()
        self.dataLoaded = True


    # Requires loadData() to be called. 
    def sortPortfolio(self):
        sortedPortfolio = sorted(self.portfolio.items(), key = lambda coin: float(coin[1][2]), reverse = True)
        sortedPortfolio = dict(sortedPortfolio)
        
        self.portfolio = sortedPortfolio
        
    # Prints assets and all details of portfolio into terminal 
    def showAssets(self):

        if not self.dataLoaded: self.loadData()

        print("\nShowing your assets in " + "\033[4m" + self.accountName + "\033[0m" + ":\n")

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
        print("Total Balance in " + '\033[4m' + self.accountName + "\033[0m" + ": " + self.totalBalance() + "\n")

    def portfolioToDataframe(self):
        
        if not self.dataLoaded: self.loadData()

        current_time = datetime.now().strftime("%m-%d-%Y %H:%M")

        dataframe = {
            'Symbol':[key for key in self.portfolio],
            'Name':[value[0] for value in self.portfolio.values()],
            'Amount':[value[1] for value in self.portfolio.values()],
            f'Balance at {current_time}': [value[2] for value in self.portfolio.values()],
            f'Price at {current_time}':[value[3] for value in self.portfolio.values()]
        }

        return dataframe


from collections import defaultdict
import pandas as pd
import xlsxwriter
from io import BytesIO

# Uses OOP Principles like Inheritance and Composition 
class MasterPortfolio(Portfolio):
    
    def __init__(self, accounts):
        if type(accounts) != list or type(accounts[0]) != Portfolio: raise TypeError()

        self.accounts = accounts

        self.exchangeData = defaultdict(list)
        self.balances = defaultdict(float)
        self.generateBalances()

        self.portfolio = dict(self.balances)
        super().__init__("Master", self.portfolio)

    def generateBalances(self):
        for account in self.accounts:
            accountPortfolio = account.portfolio
            for coin in accountPortfolio:

                if accountPortfolio[coin] == 0: continue

                if type(accountPortfolio[coin]) == list:
                    self.balances[coin] += float(accountPortfolio[coin][1])
                    continue

                self.balances[coin] += accountPortfolio[coin]

    def generateExchangeData(self):
        for account in self.accounts:
            portfolio = account.portfolio
            exchange = account.accountName
            for coin in portfolio:
                if portfolio[coin] == 0: continue
                self.exchangeData[coin].append(exchange)

    def loadExchangeData(self):
        for asset in self.portfolio:
            self.portfolio[asset].append(self.exchangeData[asset])

    def loadData(self):
        if self.dataLoaded: return

        self.generateExchangeData()
        super().loadData()
        self.loadExchangeData()

    # Overrided from 
    def showAssets(self):
        if not self.dataLoaded: self.loadData()

        print("\nShowing your \033[4mtotal\033[0m assets:\n")

        # Symbol | Name | Amount | Balance | Real-Time Price |  Exchanges with Asset
        header = f"{'Symbol':<5} | {'Name':<25} | {'Amount':<12} | {'Balance':<11} | {'Real-Time Price':<15} | {'Exchanges with Asset':<20}"
        print(header)
        print('-'*110)
        for key, value in self.portfolio.items():
            symbol = key
            name = value[0]
            amount = round(float(value[1]), 5)
            balance = round(float(value[2]), 4)
            price = round(float(value[3]), 4)
            exchanges = value[4]
            print(f"{symbol:<6} | {name:<25} | {amount:<12} | ${balance:<10} | ${price:<14} | {str(exchanges)}")
        print()
        print(f"Total Balance: {self.totalBalance()}")
        for account in self.accounts:
            account.loadData()
            print(f"{account.accountName}: {account.totalBalance()}")
        print()

    def portfolioToDataframe(self):
        dataframe = super().portfolioToDataframe()

        dataframe['Exchanges with Asset'] = [value[4] for value in self.portfolio.values()]

        return dataframe


    def pandasToExcel_local(self):
        print("Exporting Excel file.\n")

        if not self.dataLoaded: self.loadData()

        current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
        fileName = f'/Users/kyancox/Downloads/output {current_time}.xlsx'
        
        with pd.ExcelWriter(fileName, engine='xlsxwriter') as writer:
            masterDF = pd.DataFrame(self.portfolioToDataframe())
            masterDF.to_excel(writer, sheet_name = 'Master', index=False)

            total_balance = float(self.totalBalance().replace("$", "").replace(" USD", ""))
            balance_column = 3
            next_row = len(masterDF) + 2
            worksheet = writer.sheets['Master']
            workbook = writer.book
            total_balance_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True})

            worksheet.write(next_row, balance_column, total_balance, total_balance_format)
            worksheet.write(next_row, balance_column - 1, "Total Balance:", total_balance_format)

            currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': False})

            for column_width in [("A:A", 10), ("B:B", 20), ("C:C", 15), ("D:D", 25, currency_format), ("E:E", 25, currency_format), ("F:F", 25)]:
                writer.sheets['Master'].set_column(*column_width)

            for account in self.accounts:
                account.loadData()
                accountDF = pd.DataFrame(account.portfolioToDataframe())
                accountDF.to_excel(writer, sheet_name=account.accountName, index=False)

                total_balance = float(account.totalBalance().replace("$", "").replace(" USD", ""))
                worksheet = writer.sheets[account.accountName]
                next_row = len(accountDF) + 2

                worksheet.write(next_row, balance_column, total_balance, total_balance_format)
                worksheet.write(next_row, balance_column - 1, "Total Balance:", total_balance_format)

                for column_width in [("A:A", 10), ("B:B", 20), ("C:C", 15), ("D:D", 25, currency_format), ("E:E", 25, currency_format)]:
                    writer.sheets[account.accountName].set_column(*column_width)

        print("Export complete.\n")

    def pandasToExcel_api(self):
        print("Preparing Excel file for downlaod.\n")

        if not self.dataLoaded: self.loadData()

        # current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
        # fileName = f'/Users/kyancox/Downloads/output {current_time}.xlsx'

        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            masterDF = pd.DataFrame(self.portfolioToDataframe())
            masterDF.to_excel(writer, sheet_name = 'Master', index=False)

            total_balance = float(self.totalBalance().replace("$", "").replace(" USD", ""))
            balance_column = 3
            next_row = len(masterDF) + 2
            worksheet = writer.sheets['Master']
            workbook = writer.book
            total_balance_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': True})

            worksheet.write(next_row, balance_column, total_balance, total_balance_format)
            worksheet.write(next_row, balance_column - 1, "Total Balance:", total_balance_format)

            currency_format = workbook.add_format({'num_format': '$#,##0.00', 'bold': False})

            for column_width in [("A:A", 10), ("B:B", 20), ("C:C", 15), ("D:D", 25, currency_format), ("E:E", 25, currency_format), ("F:F", 25)]:
                writer.sheets['Master'].set_column(*column_width)

            for account in self.accounts:
                account.loadData()
                accountDF = pd.DataFrame(account.portfolioToDataframe())
                accountDF.to_excel(writer, sheet_name=account.accountName, index=False)

                total_balance = float(account.totalBalance().replace("$", "").replace(" USD", ""))
                worksheet = writer.sheets[account.accountName]
                next_row = len(accountDF) + 2

                worksheet.write(next_row, balance_column, total_balance, total_balance_format)
                worksheet.write(next_row, balance_column - 1, "Total Balance:", total_balance_format)

                for column_width in [("A:A", 10), ("B:B", 20), ("C:C", 15), ("D:D", 25, currency_format), ("E:E", 25, currency_format)]:
                    writer.sheets[account.accountName].set_column(*column_width)

        output.seek(0)

        print("Export complete.\n")
        return output
