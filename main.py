from common.model import GnuBook
from config.paths import GNU_CASH_FILE
from visualize.expenses import run


def update_zerodha():
    book = GnuBook(GNU_CASH_FILE, readonly=False)
    filename = "/Users/dex/Downloads/holdings.csv"
    book.import_zerodha_holdings(filename)
    book.save()


if __name__ == "__main__":
    update_zerodha()
