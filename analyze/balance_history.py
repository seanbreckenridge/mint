from typing import Dict, Set, Tuple, List
from datetime import datetime
from itertools import chain

import click
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from scipy import stats
from tzlocal import get_localzone

from budget import data, Snapshot

tz = get_localzone()

# get all balances from one snapshot
def assets(s: Snapshot) -> pd.DataFrame:
    def invert_credit_card(df_row):
        if df_row["account_type"] == "credit card":
            df_row["current"] = df_row["current"] * -1
        return df_row

    df = pd.DataFrame.from_dict(s.accounts)
    # invert credit card balances
    return df.apply(invert_credit_card, axis=1)


def remove_outliers(account_snapshots) -> List[Tuple[pd.DataFrame, datetime]]:
    """
    remove outlier snapshots (ones that might have happened while
    transfers were happening between different accounts)
    """

    click.echo("Processing {} snapshots...".format(len(account_snapshots)))
    # get data
    acc_data: List[Tuple[pd.DataFrame, datetime]] = [
        (assets(s), s.at) for s in account_snapshots
    ]
    df: pd.DataFrame = pd.DataFrame.from_dict(
        [{"sum": d[0]["current"].sum(), "at": d[1]} for d in acc_data]
    )

    # make dates indexes
    df.index = df["at"]
    df.drop(["at"], axis=1, inplace=True)

    # create sums for each snapshot
    dates: np.array = np.array([d.timestamp() for d in df.index])
    vals: np.array = np.array(df["sum"])

    # linear regression
    # y: money, x: dates
    slope, intercept, _, _, _ = stats.linregress(dates, vals)

    # calculate expected based on slope and intercept
    regression_y: np.array = intercept + slope * dates

    # difference between expected and actual
    residuals: np.array = vals - regression_y
    residual_zscores: np.array = stats.zscore(residuals)
    # get indices of items that are further than 1.5 deviations away
    outlier_indices: np.array = np.where(residual_zscores > 1.5)[0]

    # remove those from dates/vals
    # dates_cleaned = np.delete(dates, outlier_indices)
    # vals_cleaned = np.delete(vals, outlier_indices)

    # cleaned snapshot data
    acc_clean: List[Tuple[pd.DataFrame, datetime]] = [
        a for i, a in enumerate(acc_data) if i not in outlier_indices
    ]
    # for index in outlier_indices:
    # print("Removing outlier value ({}) :\n {}".format(residuals[index], acc_data[index]))
    # pass
    click.echo("Removed {} outlier snapshots.".format(len(acc_data) - len(acc_clean)))
    return acc_clean


def graph_account_balances(account_snapshots, graph: bool) -> None:
    """
    plot each account across the git hitsory
    """

    # clean data
    acc_clean = remove_outliers(account_snapshots)

    plt.style.use("dark_background")
    # graph each data point
    fig, ax = plt.subplots(figsize=(18, 10))

    # get all account names
    account_names: Set[str] = set(
        chain(*[list(a[0]["account"].values) for a in acc_clean])
    )
    # create empty account data arrays for each timestamp
    account_history: Dict[str, np.array] = {
        n: np.zeros(len(acc_clean)) for n in account_names
    }
    # convert to timestamp and back to remove git timestamp info
    secs: np.array = np.array(
        [tz.localize(datetime.fromtimestamp(sn[1].timestamp())) for sn in acc_clean]
    )
    for i, sn in enumerate(acc_clean):
        ad: pd.DataFrame = sn[0]

        # loop over rows and add to account_history, to create 'line graphs' for each item
        for _, row in ad.iterrows():
            account_history[row["account"]][i] = row["current"]

    for acc, acc_list in account_history.items():
        ax.plot(secs, acc_list, label=acc)

    ax.xaxis.set_major_formatter(mdate.DateFormatter("%d-%m-%y %H:%M:%S"))
    ax.yaxis.set_major_formatter("${x:,}")
    fig.autofmt_xdate()

    plt.legend(loc="upper left")
    plt.xlabel("Date")
    plt.ylabel("Account Balance")

    to_file = "/tmp/balance_history.png"
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
