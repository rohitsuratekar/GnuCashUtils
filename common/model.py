"""
GnuCash Book model
"""

from typing import List

import pandas as pd
from piecash import open_book, Account, Commodity, Book, Transaction, Split, Price
import datetime

pd.options.display.max_columns = None


class _CommonProperties:
    def __init__(self, filename, **kwargs):
        super().__init__()
        self.book = open_book(filename, **kwargs)  # type: Book

    def _get_base_account(self, name):
        return self.book.root_account.children(name=name)

    @property
    def currency(self) -> Commodity:
        return self.book.default_currency

    @property
    def assets(self) -> Account:
        return self._get_base_account("Assets")

    @property
    def expenses(self) -> Account:
        return self._get_base_account("Expenses")

    @property
    def equity(self) -> Account:
        return self._get_base_account("Equity")

    @property
    def liabilities(self) -> Account:
        return self._get_base_account("Liabilities")

    @property
    def transactions(self) -> List[Transaction]:
        return self.book.transactions

    @property
    def commodities(self) -> List[Commodity]:
        return self.book.commodities

    @property
    def stocks(self) -> Account:
        return self.assets.children(name="Equity Investments").children(name="Stocks")

    def save(self):
        self.book.save()


class GnuBook(_CommonProperties):
    NAMESPACE_STOCK = "Stocks"
    NAMESPACE_BONDS = "Bonds"

    def create_new_stock(self, data: dict):
        """
        Create new stocks for book opening
        :param data: Dictionary of relavant data
        """
        symbol = data["symbol"]
        fullname = data["fullname"]
        isin_id = data["isin"]
        cost = data["cost"]  # Purchase Price
        qt = data["quantity"]  # Quantity of shares
        ltp = data["ltp"]  # Last traded value

        # Get reference to Opening Balance
        eq_acc = self.equity.children(name="Opening Balances")
        # Create new Commodity
        new_com = Commodity(namespace=self.NAMESPACE_STOCK, mnemonic=symbol,
                            fraction=1, fullname=fullname, cusip=isin_id)
        self.book.add(new_com)
        # Create new account
        acc = Account(
            name=symbol, type="STOCK",
            description=fullname,
            parent=self.stocks, commodity=new_com,
        )
        self.book.add(acc)

        # Create transaction for initial shares
        new_tr = Transaction(
            currency=self.currency,
            description="Carry forward from FY2022",
            splits=[
                Split(account=eq_acc, value=f"-{qt * cost}"),
                Split(account=acc, value=f"{qt * cost}", quantity=qt)
            ]
        )
        self.book.add(new_tr)
        # Add latest price (Last traded price)
        price = Price(
            commodity=new_com, currency=self.currency,
            date=datetime.date.today(), value=f"{ltp}", type="last"
        )
        self.book.add(price)

    def create_new_bonds(self, data):
        symbol = data["symbol"]
        segment = data["segment"]
        isin_id = data["isin"]
        cost = data["cost"]  # Purchase Price
        qt = data["quantity"]  # Quantity of shares
        ltp = data["ltp"]  # Last traded value

        # Get reference to Opening Balance
        eq_acc = self.equity.children(name="Opening Balances")

        # Create new Commodity
        new_com = Commodity(namespace=self.NAMESPACE_BONDS, mnemonic=symbol,
                            fraction=1, fullname=f"{segment} - {isin_id}", cusip=isin_id)

        self.book.add(new_com)

        if segment == "SGB":
            parent = self.assets.children(name="Fixed Income Investments").children(name="Sovereign Gold Bonds")
        elif segment == "TB":
            parent = self.assets.children(name="Fixed Income Investments").children(name="Debt Instruments")
        else:
            raise ValueError(f"Unknown segment : {segment}")

        # Create new account
        acc = Account(
            name=symbol, type="STOCK",
            description=f"{segment} - {isin_id}",
            parent=parent, commodity=new_com,
        )
        self.book.add(acc)

        # Create transaction for initial shares
        new_tr = Transaction(
            currency=self.currency,
            description="Carry forward from FY2022",
            splits=[
                Split(account=eq_acc, value=f"-{qt * cost}"),
                Split(account=acc, value=f"{qt * cost}", quantity=qt)
            ]
        )
        self.book.add(new_tr)
        # Add latest price (Last traded price)
        price = Price(
            commodity=new_com, currency=self.currency,
            date=datetime.date.today(), value=f"{ltp}", type="last"
        )
        self.book.add(price)
