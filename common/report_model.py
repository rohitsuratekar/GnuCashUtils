"""
Model to extract the data information
"""
from common.model import GnuBook
from piecash import open_book, Account, Commodity, Book, Transaction, Split, Price


class AssetReport(GnuBook):

    @property
    def stocks(self) -> Account:
        return self.assets.children(name="Equity Investments").children(name="Stocks")

    @property
    def mfs(self) -> Account:
        return self.assets.children(name="Equity Investments").children(name="Mutual Funds")

    @property
    def fd(self) -> Account:
        return self.assets.children(name="Fixed Income Investments").children(name="Fixed Deposits")

    @property
    def sgb(self) -> Account:
        return self.assets.children(name="Fixed Income Investments").children(name="Sovereign Gold Bonds")

    @property
    def debt(self) -> Account:
        return self.assets.children(name="Fixed Income Investments").children(name="Debt Instruments")

    @property
    def ppf(self) -> Account:
        return self.assets.children(name="Fixed Income Investments").children(name="Public Provident Fund")

    @property
    def epf(self) -> Account:
        return self.assets.children(name="Fixed Income Investments").children(name="Employee Provident Fund")

    @property
    def savings(self) -> Account:
        return self.assets.children(name="Cash and Equivalents").children(name="Saving Accounts")

    @property
    def zerodha(self) -> Account:
        return self.assets.children(name="Wallets").children(name="Zerodha")

    @staticmethod
    def _pad_word(word, max_length):
        return word + "".join(["."] * (max_length - len(word) + 2))

    def show_savings_cash(self):
        print("= Saving Accounts ========")
        max_word = max([len(x.name) for x in self.savings.children])
        for child in self.savings.children:
            print(f"  {self._pad_word(child.name, max_word)} INR {child.get_balance()}")

    def show_deposits(self):
        print("= Fixed Deposits ========")
        max_word = max([len(x.name) for x in self.fd.children])
        for child in self.fd.children:
            print(f"  {self._pad_word(child.name, max_word)} INR {round(child.get_balance(), 2)}")

    def show_others(self):
        print("= Other =================")
        accounts = [self.ppf, self.epf, self.stocks, self.mfs, self.zerodha]
        max_word = max([len(x.name) for x in accounts] + [len("Bonds")])
        for child in accounts:
            print(f"  {self._pad_word(child.name, max_word)} INR {round(child.get_balance(), 2)}")

        bonds = self.sgb.get_balance() + self.debt.get_balance()
        print(f"  {self._pad_word('Bonds', max_word)} INR {round(bonds, 2)}")

    def display_all(self):
        self.show_savings_cash()
        self.show_deposits()
        self.show_others()
