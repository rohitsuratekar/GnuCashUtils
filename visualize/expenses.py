"""
Visualize expenses from GNUCash exported csv
"""
import pandas as pd
from piecash import Split, Account

from common.model import GnuBook
from config.paths import GNU_CASH_FILE

pd.options.display.max_columns = None


def run():
    book = GnuBook(GNU_CASH_FILE, readonly=True)
    all_income = []
    for trans in book.transactions:
        for sp1 in trans.splits:
            sp = sp1  # type: Split
            ac = sp.account  # type: Account
            # print(sp.account)
            if ac.type == "INCOME":
                all_income.append({
                    "Date": trans.enter_date,
                    "Name": ac.fullname,
                    "Value": - float(sp.value)})

    all_income = pd.DataFrame(all_income)
    all_income["Account"] = all_income["Name"].map(lambda x: x.split(":")[1])
    all_income["Month"] = all_income["Date"].map(lambda x: x.strftime("%b-%y"))
    all_income = all_income.groupby(["Month", "Account"])["Value"].sum().reset_index()
    print(all_income)
