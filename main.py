import pandas as pd

from common.model import GnuBook
from config.paths import GNU_CASH_FILE

if __name__ == "__main__":
    book = GnuBook(GNU_CASH_FILE, readonly=False)
    filename = "/Users/dex/Downloads/holdings.csv"
