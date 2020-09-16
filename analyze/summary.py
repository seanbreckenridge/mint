from datetime import date, timedelta
from typing import Union, Any

import click
import pandas as pd
from pyfiglet import figlet_format

import budget


def banner(msg):
    click.echo("```")
    click.secho(figlet_format(msg, "thin"), fg="blue")
    click.echo("```")


def hr():
    click.echo("\n{}\n".format("-" * 10))


def color(msg: Any, color: str = "green"):
    return click.style(f"*{msg}*", fg=color)


# helper function to print a table
def print_df(df, *, index=False, rename_cols={}, sort_by=None, ascending=False):
    if sort_by is not None and isinstance(sort_by, list):
        df = df.sort_values(sort_by, ascending=ascending)
    click.echo(df.rename(columns=rename_cols).to_markdown(index=index))


def account_summary(account_snapshots):
    hr()
    account = account_snapshots[-1].accounts
    ### ACCOUNT SUMMARY
    _af = pd.DataFrame.from_dict(account_snapshots[-1].accounts)
    # remove fields
    af = _af.drop(["currency", "available", "limit", "institution"], axis=1)
    # remove credit cards https://thispointer.com/python-pandas-how-to-drop-rows-in-dataframe-by-conditions-on-column-values/
    no_credit_af = af.drop(af[af["account_type"] == "credit card"].index)

    banner("Accounts")
    hr()

    # print account balances
    print_df(no_credit_af, rename_cols={"account_type": "type"}, sort_by=["current"])
    click.echo("\nTotal Balance: {}\n".format(color(no_credit_af["current"].sum())))

    hr()

    # credit cards
    credit_cards = _af.drop(af[af["account_type"] != "credit card"].index)
    credit_cards.drop(
        ["currency", "available", "institution", "account_type"], axis=1, inplace=True
    )

    credit_card_total = credit_cards["current"].sum()
    if credit_card_total > 0.5:
        banner("Credit Cards")
        print_df(credit_cards, sort_by=["current"])
        click.echo(
            "\nCredit Card Usage: {}\n".format(
                click.style(
                    f"*{credit_card_total}*",
                    fg="red" if credit_card_total > 100 else "green",
                )
            )
        )
    else:
        click.secho("**No credit card usage!**", fg="green")

    return _af


today = date.today()


def _get_timeframe(transactions, timeframe):
    return transactions[today - transactions["on"] < timeframe]


def describe_spending(
    transactions,
    title: str,
    by: str = "meta_category",
    print_count: Union[int, bool] = 10,
    display_categories=True,
):
    hr()
    sorted_transactions = transactions.sort_values(["amount"], ascending=False).drop(
        ["meta_category"], axis=1
    )
    if print_count is True:
        click.echo(f"## All transactions for {title}\n")
        print_df(sorted_transactions)
    else:
        click.echo(f"## Largest transactions for {title}\n")
        print_df(sorted_transactions.head(print_count))

    hr()

    total_spending = sorted_transactions["amount"].sum()
    if display_categories:
        # group by categories
        by_meta_category = (
            transactions.groupby([by]).sum().sort_values(["amount"], ascending=False)
        )
        # add percentage
        by_meta_category["percent"] = by_meta_category["amount"].apply(
            lambda am: f"{am/total_spending * 100:.1f}%"
        )
        # replace names of index to be more generic
        by_meta_category.index.name = "category"
        print(end="\n")  # print a newline
        print_df(by_meta_category, sort_by=["amount"], index=True)

    click.echo("\n{} spending: {}\n\n".format(title, color(f"{total_spending:.2f}")))
    return sorted_transactions


def recent_spending(transactions):
    _tr = pd.DataFrame.from_dict(transactions)

    # remove transfers between accounts/income
    spending = pd.DataFrame(_tr[_tr["meta_category"] != "Transfer"])

    all_time = spending
    last_year = _get_timeframe(spending, timedelta(days=365))
    last_3_months = _get_timeframe(spending, timedelta(days=90))
    last_30_days = _get_timeframe(spending, timedelta(days=30))

    banner("Transactions")

    describe_spending(all_time, "full transaction history", print_count=True)
    describe_spending(last_year, "last year", print_count=80)
    # use specific categories for 3 months/30 days
    describe_spending(last_3_months, "last 3 months", print_count=60, by="category")
    describe_spending(
        last_30_days, "last 30 days", print_count=True, by="category"
    )  # print all transactions in last 30 days
    return spending


@click.command()
@click.option("--repl", is_flag=True, default=False)
def main(repl):
    account_snapshots, transactions = budget.data()

    spend = recent_spending(transactions)
    acc = account_summary(account_snapshots)

    if repl:
        click.secho("Use 'acc' and 'spend' to interact", fg="green")
        import IPython

        IPython.embed()


if __name__ == "__main__":
    main()
