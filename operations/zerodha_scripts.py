"""
Scripts based on Zerodha data
"""

from common.model import GnuBook
from operations.stocks_functions import add_stocks_to_book, add_bonds_to_book, update_last_traded_values

FILE_SYMBOL_MAP = "/Users/dex/Documents/Rohit/Softwares/PythonProjects/GnuCashUtils/data/symbol_mapping.csv"


def add_to_new_book(gnu_file, stock_file):
    """
    Adds new stocks from Zerodha holdings list
    Use this for newly created books
    """
    gnu_book = GnuBook(gnu_file, readonly=False)
    add_stocks_to_book(stock_file=stock_file,
                       gnu_book=gnu_book,
                       symbol_map=FILE_SYMBOL_MAP)
    add_bonds_to_book(stock_file=stock_file,
                      gnu_book=gnu_book,
                      symbol_map=FILE_SYMBOL_MAP)

    gnu_book.save()


def update_from_zerodha(gnu_file, stock_file):
    """
    Updates stock prices from Zerodha holdings csv
    """
    gnu_book = GnuBook(gnu_file, readonly=False)
    update_last_traded_values(stock_file=stock_file,
                              gnu_book=gnu_book,
                              symbol_map=FILE_SYMBOL_MAP)

    gnu_book.save()
