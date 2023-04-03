"""
Scripts related to generating new book
"""

import datetime

import pandas as pd
from piecash import Price

from common.model import GnuBook
from operations.data_fetching import get_eq_data, get_reit_data

SK_SYMBOL = "Instrument"
SK_QUANTITY = "Qty."
SK_AVG_COST = "Avg. cost"
SK_LTP = "LTP"
SK_NAME = "NAME OF COMPANY"
SK_ISIN = "ISIN NUMBER"

MP_SYMBOL = "symbol"
MP_MAPPING_SYMBOL = "mapping_symbol"
MP_SEGMENT = "segment"


def add_stocks_to_book(*, stock_file: str, gnu_book: GnuBook, symbol_map=None):
    """
    Adds stocks to new book opening.
    Note - Book is only adjusted not saved.
    :param stock_file: Zerodha holdings csv
    :param gnu_book: GnuBook object
    :param symbol_map: Symbol mapping file
    """
    st_df = pd.read_csv(stock_file)
    eq_df = get_eq_data().set_index("SYMBOL")
    rt_df = get_reit_data().set_index("SYMBOL")
    sym_map = {}
    if symbol_map:
        sym_map = pd.read_csv(symbol_map).set_index(MP_SYMBOL)
        sym_map = sym_map[MP_MAPPING_SYMBOL].to_dict()
    for _, row in st_df.iterrows():
        sym = row[SK_SYMBOL]
        data = {
            "symbol": sym,
            "quantity": row[SK_QUANTITY],
            "cost": row[SK_AVG_COST],
            "ltp": row[SK_LTP]
        }

        if sym in sym_map:
            sym = sym_map[sym]
        if sym in eq_df.index:
            data["fullname"] = eq_df.loc[sym][SK_NAME]
            data["isin"] = eq_df.loc[sym][SK_ISIN]
        elif sym in rt_df.index:
            data["fullname"] = rt_df.loc[sym][SK_NAME]
            data["isin"] = rt_df.loc[sym][SK_ISIN]
        else:
            print(f"Unable to find : {sym} for stock addition")
            continue
        gnu_book.create_new_stock(data)


def add_bonds_to_book(*, stock_file: str, gnu_book: GnuBook, symbol_map: str):
    """
    Adds bonds to new book opening.
    Note - Book is only adjusted not saved.
    :param stock_file: Zerodha holdings csv
    :param gnu_book: GnuBook object
    :param symbol_map: Symbol mapping file
    """
    st_df = pd.read_csv(stock_file)
    symbol_map = pd.read_csv(symbol_map)
    symbol_map = symbol_map[symbol_map[MP_SEGMENT].isin(["SGB", "TB"])].set_index(MP_SYMBOL)
    for _, row in st_df.iterrows():
        sym = row[SK_SYMBOL]
        if sym not in symbol_map.index:
            continue
        data = {
            "symbol": symbol_map.loc[sym][MP_MAPPING_SYMBOL],
            "isin": sym,
            "quantity": row[SK_QUANTITY],
            "cost": row[SK_AVG_COST],
            "ltp": row[SK_LTP],
            "segment": symbol_map.loc[sym][MP_SEGMENT]
        }
        gnu_book.create_new_bonds(data)


def update_last_traded_values(*, stock_file: str, gnu_book: GnuBook, symbol_map=None):
    """
    Updates the last traded values based on Zerodha holdings
    Note - Book is only adjusted not saved.
    :param stock_file: Zerodha holdings csv
    :param gnu_book: GnuBook object
    :param symbol_map: Symbol mapping file
    """
    st_df = pd.read_csv(stock_file).set_index(SK_SYMBOL)
    symbol_map = pd.read_csv(symbol_map).set_index(MP_MAPPING_SYMBOL)[MP_SYMBOL].to_dict()

    for comm in gnu_book.commodities:
        c_sym = comm.mnemonic
        if c_sym == "INR":  # Ignore Currency
            continue

        if c_sym in symbol_map and c_sym not in st_df.index:
            c_sym = symbol_map[c_sym]

        if c_sym in st_df.index:
            c_data = st_df.loc[c_sym]
            price = Price(
                commodity=comm, currency=gnu_book.currency,
                date=datetime.date.today(),
                value=str(round(c_data[SK_LTP], 2)),
                type="last"
            )
            gnu_book.book.add(price)
            print(f"Price updated for {c_sym}")
        else:
            print(f"Ignoring {c_sym}")
