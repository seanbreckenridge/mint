from typing import Iterator, Dict
from datetime import datetime
from itertools import chain

import click
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

from scipy import stats

from budget import data, Snapshot

# get all balances from one snapshot
def assets(s: Snapshot) -> pd.DataFrame:
    def invert_credit_card(df_row):
        if df_row["account_type"] == "credit card":
            df_row["current"] = df_row["current"] * -1
        return df_row

    df = pd.DataFrame.from_dict(s.accounts)
    # invert credit card balances
    return df.apply(invert_credit_card, axis=1)


def graph_account_balances(account_snapshots, graph: bool) -> Iterator[Snapshot]:
    """
    remove outlier snapshots (ones that might have happened while
    transfers were happening between different accounts)

    after removing those, plot each account across the git hitsory
    """

    click.echo("Processing {} snapshots...".format(len(account_snapshots)))
    # get data
    acc_data = [(assets(s), s.at) for s in account_snapshots]
    df = pd.DataFrame.from_dict(
        [{"sum": d[0]["current"].sum(), "at": d[1]} for d in acc_data]
    )

    # make dates indexes
    df.index = df["at"]
    df.drop(["at"], axis=1, inplace=True)

    # create sums for each snapshot
    dates = np.array([d.timestamp() for d in df.index])
    vals = np.array(list(chain(*df.values.tolist())))

    # linear regression
    # y: money, x: dates
    slope, intercept, _, _, _ = stats.linregress(dates, vals)

    # calculate expected based on slope and intercept
    regression_y = intercept + slope * dates

    # difference between expected and actual
    residuals = vals - regression_y
    mean_difference = np.abs(residuals).mean()

    # TODO: use stdev?
    # get indices of items that are further from 2 the mean difference
    more_than = np.vectorize(lambda v: abs(v) > mean_difference * 2.5)
    more_than_indices = np.where(more_than(residuals) == True)[0]

    # remove those
    # dates_cleaned = np.delete(dates, more_than_indices)
    # vals_cleaned = np.delete(vals, more_than_indices)

    # cleaned snapshot data
    acc_clean = [a for i, a in enumerate(acc_data) if i not in more_than_indices]

    # for index in more_than_indices:
    # print("Removing outlier value ({}) :\n {}".format(residuals[index], acc_data[index]))
    # pass
    click.echo("Removed {} outlier snapshots.".format(len(acc_data) - len(acc_clean)))

    # graph each data point
    fig, ax = plt.subplots(figsize=(18,10))

    # get all account names
    account_names = set(chain(*[list(a[0]["account"].values) for a in acc_clean]))
    # create empty account data arrays for each timestamp
    account_history: Dict[str, np.array] = {
        n: np.zeros(len(acc_clean)) for n in account_names
    }
    # convert to timestamp and back to remove git timestamp info
    secs = np.array([datetime.fromtimestamp(sn[1].timestamp()) for sn in acc_clean])
    for i, sn in enumerate(acc_clean):
        ad: pd.DataFrame = sn[0]

        # loop over rows and add to account_history, to create 'line graphs' for each item
        for _, row in ad.iterrows():
            account_history[row["account"]][i] = row["current"]

        # ax.plot(dates_cleaned, uploaded, label="uploaded")

    for acc, acc_list in account_history.items():
        ax.plot(secs, acc_list, label=acc)

    ax.xaxis.set_major_formatter(mdate.DateFormatter("%d-%m-%y %H:%M:%S"))
    fig.autofmt_xdate()

    plt.legend(loc="upper left")
    plt.xlabel("Date")
    plt.ylabel("Account Balance")

    to_file = '/tmp/balance_history.png'
    plt.savefig(to_file)
    click.echo("Saved to {}".format(to_file))

    if graph:
        plt.show()


@click.command()
@click.option("--show", default=False, is_flag=True)
def main(show):
    account_snapshots, _ = data()
    account_snapshots.sort(key=lambda s: s.at)
    graph_account_balances(account_snapshots, show)


if __name__ == "__main__":
    main()
