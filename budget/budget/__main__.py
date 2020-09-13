from pathlib import Path

import click

from typing import List
from .transactions import Transaction, read_transactions
from .balances import generate_account_history, Snapshot


@click.command()
@click.argument("DATADIR")
def main(datadir: str):
    ddir = Path(datadir).absolute()
    assert ddir.is_dir() and ddir.exists()

    balance_history: List[Snapshot] = list(generate_account_history(ddir))
    transactions: List[Transaction] = list(read_transactions(ddir))

    click.secho("use 'balance_history' and 'transactions'", fg='green')

    import IPython

    IPython.embed()

if __name__ == "__main__":
    main()
