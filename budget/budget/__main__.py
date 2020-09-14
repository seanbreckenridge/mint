from pathlib import Path

import sys
import click

from typing import List

from .load.transactions import Transaction, read_transactions
from .load.balances import generate_account_history, Snapshot

from .cleandata.accounts import clean_data
from .cleandata.transactions.transform import transform_all as transform

from .manual import edit_manual_balances


@click.command()
@click.argument("DATADIR")
@click.option(
    "--edit-manual",
    is_flag=True,
    default=False,
    help="Edit the manual_balances.csv file",
)
def main(datadir: str, edit_manual: bool):
    ddir = Path(datadir).absolute()
    assert ddir.is_dir() and ddir.exists()

    if edit_manual:
        edit_manual_balances(ddir / "manual_balances.csv")
        sys.exit(0)

    # load in data
    balance_snapshots: List[Snapshot] = list(generate_account_history(ddir))
    transactions: List[Transaction] = list(read_transactions(ddir))

    # clean data
    balance_snapshots, transactions = clean_data(balance_snapshots, transactions)

    # transform transaction description/categories
    transactions = list(transform(transactions))

    click.secho("use 'balance_snapshots' and 'transactions'", fg="green")

    import IPython

    IPython.embed()


if __name__ == "__main__":
    main()
