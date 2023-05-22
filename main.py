"""
GnuCashUtils
Author: Rohit Suratekar (rohitsuratekar@gmail.com)

Simple utilities to handle the GNU Cash database.
Your database should be SQLight for these scripts to work
"""

from common.report_model import AssetReport
from operations.zerodha_scripts import update_from_zerodha

FILE_STOCK = "/Users/dex/Downloads/holdings.csv"
FILE_GNU_CASH = "/Users/dex/Documents/Rohit/Documents/Finance/AccountBooks/gnucash/FY2023.gnucash"


def update():
    update_from_zerodha(FILE_GNU_CASH, FILE_STOCK)


def display_asset_reports():
    AssetReport(FILE_GNU_CASH).display_all()


# display_asset_reports()
update()
