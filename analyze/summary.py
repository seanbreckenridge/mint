from datetime import date, timedelta

import click
import pandas as pd
from pyfiglet import figlet_format

import budget

def banner(msg):
    click.secho(figlet_format(msg, 'thin'), fg='blue')

def account_summary(account_snapshots):
    account = account_snapshots[-1].accounts
    ### ACCOUNT SUMMARY
    _af = pd.DataFrame.from_dict(account_snapshots[-1].accounts)
    # remove fields
    af = _af.drop(['currency', 'available', 'limit', 'institution'], axis=1)
    # remove credit cards https://thispointer.com/python-pandas-how-to-drop-rows-in-dataframe-by-conditions-on-column-values/
    no_credit_af = af.drop(af[af['account_type'] == 'credit card'].index)

    banner('Accounts')

    # print account balances
    print(no_credit_af.sort_values(['current'], ascending=False).to_string(index=False))
    click.echo("\nTotal Balance: {}\n".format(click.style(str(no_credit_af['current'].sum()), fg='green')))

    # credit cards
    credit_cards = _af.drop(af[af['account_type'] != 'credit card'].index)
    credit_cards.drop(['currency', 'available', 'institution', 'account_type'], axis=1, inplace=True)

    banner("Credit Cards")

    print(credit_cards.sort_values(['current'], ascending=False).to_string(index=False))
    credit_card_total = credit_cards['current'].sum()
    click.echo("\nCredit Card Usage: {}\n".format(click.style(str(credit_card_total), fg='red' if credit_card_total > 100 else 'green')))


    return _af


@click.command()
@click.option("--repl", is_flag=True, default=False)
def main(repl):
    account_snapshots, transactions = budget.data()

    acc = account_summary(account_snapshots)

    if repl:
        click.secho("Use 'acc'", fg='green')
        import IPython
        IPython.embed()


if __name__ == "__main__":
    main()
