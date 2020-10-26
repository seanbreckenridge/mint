import sys
from typing import List

import click

from . import data, get_data_dir, Transaction, Snapshot
from .manual import edit_manual_balances


def run_repl(
    balance_snapshots: List[Snapshot], transactions: List[Transaction]
) -> None:
    click.secho("use 'balance_snapshots' and 'transactions'", fg="green")
    import IPython  # type: ignore[import]

    IPython.embed()


@click.command()
@click.option(
    "--edit-manual",
    is_flag=True,
    default=False,
    help="Edit the manual_balances.csv file",
)
@click.option("--repl", is_flag=True, default=False, help="Use data in an IPython REPL")
def main(edit_manual: bool, repl: bool) -> None:
    ddir = get_data_dir()
    assert ddir.is_dir() and ddir.exists()

    if edit_manual:
        edit_manual_balances(ddir / "manual_balances.csv")
        sys.exit(0)

    balance_snapshots, transactions = data(ddir)
    transactions.sort(key=lambda t: t.on)

    if repl or True:  # temporary, may change if I add other entrypoints
        run_repl(balance_snapshots, transactions)
        sys.exit(0)


if __name__ == "__main__":
    main()
