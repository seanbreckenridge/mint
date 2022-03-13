import sys

import click


@click.group()
def main() -> None:
    """
    Interact with my budget!
    """
    pass


@main.command()
def edit_manual() -> None:
    """
    Edit the manual balances file
    """
    from . import get_data_dir
    from .manual import edit_manual_balances

    ddir = get_data_dir()
    assert ddir.is_dir() and ddir.exists()

    edit_manual_balances(ddir / "manual_balances.csv")
    sys.exit(0)


# TODO: split this into further commands?
@main.command()
@click.option(
    "--graph", default=False, is_flag=True, help="Show the graph of balance history"
)
@click.option("--repl", default=False, is_flag=True, help="Drop into repl")
@click.option("--df", default=False, is_flag=True, help="Use dataframe in REPL")
@click.option(
    "--debug",
    default=False,
    is_flag=True,
    help="Print duplicate transactions that are removed",
)
def accounts(graph: bool, repl: bool, df: bool, debug: bool) -> None:
    """
    Show a summary/graph of the current/past accounts balances
    """
    from . import data
    from .analyze.balance_history import graph_account_balances

    if graph:
        try:
            account_snapshots, _ = data(debug=debug)
            account_snapshots.sort(key=lambda s: s.at)
            graph_account_balances(account_snapshots, graph)
        except ModuleNotFoundError as m:
            click.echo(str(m), err=True)
            sys.exit(1)
    import IPython  # type: ignore[import]
    from .analyze import cleaned_snapshots, cleaned_snapshots_df

    click.secho("Use 'snapshots' to interact with data", fg="green")
    if df:
        snapshots = cleaned_snapshots_df()
    else:
        # TODO(sean): fix timestamp
        snapshots = list(cleaned_snapshots())  # type: ignore[assignment,arg-type]
    IPython.embed()
    sys.exit(0)


@main.command()
@click.option(
    "--repl",
    is_flag=True,
    default=False,
    help="Drop into a repl with access to the accounts/spending",
)
@click.option(
    "--debug",
    default=False,
    is_flag=True,
    help="Print duplicate transactions that are removed",
)
@click.option(
    "--include-transfers",
    default=False,
    is_flag=True,
    help="Include items classified as transfers between accounts in summary",
)
def summary(repl: bool, debug: bool, include_transfers: bool) -> None:
    """
    Prints a summary of current accounts/recent transactions
    """

    from . import data
    from .analyze.summary import recent_spending, account_summary

    account_snapshots, transactions = data(debug=debug)

    spend = recent_spending(transactions, include_transfers=include_transfers)
    acc = account_summary(account_snapshots)

    # sort by date
    spend.sort_values(["on"], inplace=True)

    if repl:
        click.secho("Use 'acc' and 'spend' to interact", fg="green")
        import IPython  # type: ignore

        IPython.embed()


if __name__ == "__main__":
    main(prog_name="budget")
