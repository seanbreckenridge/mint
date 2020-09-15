import sys
import click


from . import data, get_data_dir
from .manual import edit_manual_balances


def run_repl(balance_snapshots, transactions):
    click.secho("use 'balance_snapshots' and 'transactions'", fg="green")
    import IPython

    IPython.embed()


@click.command()
@click.option(
    "--edit-manual",
    is_flag=True,
    default=False,
    help="Edit the manual_balances.csv file",
)
@click.option("--repl", is_flag=True, default=False, help="Use data in an IPython REPL")
def main(edit_manual: bool, repl: bool):
    ddir = get_data_dir()
    assert ddir.is_dir() and ddir.exists()

    if edit_manual:
        edit_manual_balances(ddir / "manual_balances.csv")
        sys.exit(0)

    balance_snapshots, transactions = data(ddir)

    if repl or True:  # temporary, may change if I add other entrypoints
        run_repl(balance_snapshots, transactions)
        sys.exit(0)


if __name__ == "__main__":
    main()
