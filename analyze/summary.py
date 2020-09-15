from datetime import date, timedelta
from typing import Union

import click
import pandas as pd
from pyfiglet import figlet_format

import budget


def banner(msg):
    click.secho(figlet_format(msg, "thin"), fg="blue")


def account_summary(account_snapshots):
    account = account_snapshots[-1].accounts
    ### ACCOUNT SUMMARY
    _af = pd.DataFrame.from_dict(account_snapshots[-1].accounts)
    # remove fields
    af = _af.drop(["currency", "available", "limit", "institution"], axis=1)
    # remove credit cards https://thispointer.com/python-pandas-how-to-drop-rows-in-dataframe-by-conditions-on-column-values/
    no_credit_af = af.drop(af[af["account_type"] == "credit card"].index)

    banner("Accounts")

    # print account balances
    print(no_credit_af.sort_values(["current"], ascending=False).to_string(index=False))
    click.echo(
        "\nTotal Balance: {}\n".format(
            click.style(str(no_credit_af["current"].sum()), fg="green")
        )
    )

    # credit cards
    credit_cards = _af.drop(af[af["account_type"] != "credit card"].index)
    credit_cards.drop(
        ["currency", "available", "institution", "account_type"], axis=1, inplace=True
    )

    credit_card_total = credit_cards["current"].sum()
    if credit_card_total > 0:
        banner("Credit Cards")

        print(
            credit_cards.sort_values(["current"], ascending=False).to_string(
                index=False
            )
        )
        click.echo(
            "\nCredit Card Usage: {}\n".format(
                click.style(
                    str(credit_card_total),
                    fg="red" if credit_card_total > 100 else "green",
                )
            )
        )
    else:
        click.secho("No credit card usage!", fg="green")

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
    print()
    sorted_transactions = transactions.sort_values(["amount"], ascending=False)
    if print_count is True:
        click.echo(f"All transactions for {title}")
        click.echo(sorted_transactions.to_string(index=False))
    else:
        click.echo(f"Largest transactions for {title}")
        click.echo(sorted_transactions.head(print_count).to_string(index=False))

    if display_categories:
        by_meta_category = (
            transactions.groupby([by]).sum().sort_values(["amount"], ascending=False)
        )
        by_meta_category.index.name = "category"
        by_meta_category.columns = ["total"]
        click.echo(by_meta_category.sort_values(["total"], ascending=False).to_string())

    total = sorted_transactions["amount"].sum()
    click.echo(
        "\n{} spending: {}\n".format(
            title, click.style(str(f"{total:.2f}"), fg="green")
        )
    )
    print()
    return sorted_transactions


def recent_spending(transactions):
    _tr = pd.DataFrame.from_dict(transactions)

    # remove transfers between accounts/income
    spending = pd.DataFrame(_tr[_tr["meta_category"] != "Transfer"])

    last_year = _get_timeframe(spending, timedelta(days=365))
    last_3_months = _get_timeframe(spending, timedelta(days=90))
    last_30_days = _get_timeframe(spending, timedelta(days=30))

    banner("Transactions")

    describe_spending(last_year, "last year", print_count=80)
    # use specific categories for 3 months/30 days
    describe_spending(last_3_months, "last 3 months", print_count=60, by="category")
    describe_spending(
        last_30_days, "last 30 days", print_count=True, by="category"
    )  # print all transactions in last 30 days


@click.command()
@click.option("--repl", is_flag=True, default=False)
def main(repl):
    account_snapshots, transactions = budget.data()

    tr = recent_spending(transactions)
    acc = account_summary(account_snapshots)

    if repl:
        click.secho("Use 'acc' and 'tr' to interact", fg="green")
        import IPython

        IPython.embed()


if __name__ == "__main__":
    main()
