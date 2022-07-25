"""
Common utility model
"""
import datetime
from typing import List

import pandas as pd
from piecash import open_book, Account, Commodity, Book, Transaction, Price, Split

from config.paths import NSE_SYMBOL_FILE


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
        return self.assets.children(name="Stocks")

    def save(self):
        self.book.save()


class GnuBook(_CommonProperties):
    STOCK_KEY = "Market"
    MF_KEY = "MF"

    def __repr__(self):
        return f"GnuBook({self.book.uri})"

    def get_savings_account(self, name) -> Account:
        return self.assets.children(name="Savings Accounts").children(name=name)

    def _delete_all_stocks(self):
        # First delete all transactions related to all stocks
        for tr in self.transactions:
            all_splits = [x.account.parent for x in tr.splits]
            if self.stocks in all_splits:
                self.book.delete(tr)

        # Delete all accounts associated with it
        for m in self.stocks.children:
            self.book.delete(m)

        # Delete all commodities
        for c in self.commodities:
            if c.namespace != "CURRENCY":
                self.book.delete(c)

    def _create_stock(self, sym, cost, qt, ltp):
        nse_df = pd.read_csv(NSE_SYMBOL_FILE)
        nse_df = nse_df.set_index("SYMBOL")["NAME OF COMPANY"].to_dict()
        eq_acc = self.equity.children(name="Opening Balances")
        new_com = Commodity(namespace=self.STOCK_KEY, mnemonic=sym,
                            fraction=1, fullname=nse_df[sym])
        self.book.add(new_com)
        acc = Account(
            name=sym, type="STOCK",
            parent=self.stocks, commodity=new_com,
        )
        self.book.add(acc)
        new_tr = Transaction(
            currency=self.currency,
            description="Carry Forward",
            splits=[
                Split(account=eq_acc, value=f"-{qt * cost}"),
                Split(account=acc, value=f"{qt * cost}", quantity=qt)
            ]
        )
        self.book.add(new_tr)
        price = Price(
            commodity=new_com, currency=self.currency,
            date=datetime.date.today(), value=f"{ltp}", type="last"
        )
        self.book.add(price)

    def create_stocks_from_zerodha_export(self, filename):
        df = pd.read_csv(filename)
        coms = {}
        for c in self.commodities:
            key = f"{c.namespace}:{c.mnemonic}"
            coms[key] = c

        for _, row in df.iterrows():
            sym = row["Instrument"]
            qt = row["Qty."]
            cost = round(row["Avg. cost"], 2)
            ltp = round(row["LTP"], 2)
            key = f"{self.STOCK_KEY}:{sym}"
            if key not in coms:
                self._create_stock(sym, cost, qt, ltp)
            else:
                Price(
                    commodity=coms[key], currency=self.currency,
                    date=datetime.date.today(), value=f"{ltp}", type="last"
                )

    def run(self):
        self.create_stocks_from_zerodha_export("/Users/dex/Downloads/holdings.csv")
        # self._delete_all_stocks()
        self.save()
