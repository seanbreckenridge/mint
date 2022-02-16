from typing import Dict, Set, Tuple, List
from datetime import datetime
from itertools import chain

import click
import numpy as np  # type: ignore[import]
from numpy.typing import NDArray
import pandas as pd  # type: ignore[import]
import matplotlib.pyplot as plt  # type: ignore[import]
import matplotlib.dates as mdate  # type: ignore[import]
import matplotlib.ticker as tick  # type: ignore[import]
from scipy import stats  # type: ignore[import]
from tzlocal import get_localzone  # type: ignore[import]

from ..load.balances import Snapshot

tz = get_localzone()

# convert to timestamp and back to remove git timestamp info
def fix_timestamp(t: datetime) -> datetime:
    dt = tz.localize(datetime.fromtimestamp(t.timestamp()))
    assert isinstance(dt, datetime)
    return dt


def invert_credit_card(df_row):  # type: ignore
    if df_row["account_type"] == "credit card":
        df_row["current"] = df_row["current"] * -1
    return df_row


# get all balances from one snapshot
def assets(s: Snapshot) -> pd.DataFrame:

    df = pd.DataFrame.from_dict(s.accounts)
    # invert credit card balances
    return df.apply(invert_credit_card, axis=1)


SnapshotData = List[Tuple[pd.DataFrame, datetime]]


NDFloatArr = NDArray[np.float64]


def remove_outliers(
    account_snapshots: List[Snapshot], print: bool = True
) -> SnapshotData:
    """
    remove outlier snapshots (ones that might have happened while
    transfers were happening between different accounts)
    """

    if print:
        click.echo("Processing {} snapshots...".format(len(account_snapshots)))
    # get data
    acc_data: SnapshotData = [(assets(s), s.at) for s in account_snapshots]
    df: pd.DataFrame = pd.DataFrame.from_dict(
        [{"sum": d[0]["current"].sum(), "at": d[1]} for d in acc_data]
    )

    # make dates indexes
    df.index = df["at"]
    df.drop(["at"], axis=1, inplace=True)

    # create sums for each snapshot
    dates: NDFloatArr = np.array([d.timestamp() for d in df.index])
    vals: NDFloatArr = np.array(df["sum"])

    # linear regression
    # y: money, x: dates
    slope, intercept, _, _, _ = stats.linregress(dates, vals)

    # calculate expected based on slope and intercept
    regression_y: NDFloatArr = intercept + slope * dates

    # difference between expected and actual
    residuals: NDFloatArr = vals - regression_y
    residual_zscores: NDFloatArr = stats.zscore(residuals)
    # get indices of items that are further than 1.5 deviations away
    outlier_indices: NDArray[np.int64] = next(iter(np.where(residual_zscores > 1.5)))

    # remove those from dates/vals
    # dates_cleaned = np.delete(dates, outlier_indices)
    # vals_cleaned = np.delete(vals, outlier_indices)

    # cleaned snapshot data
    acc_clean: SnapshotData = [
        a for i, a in enumerate(acc_data) if i not in outlier_indices
    ]
    # for index in outlier_indices:
    # print("Removing outlier value ({}) :\n {}".format(residuals[index], acc_data[index]))
    # pass
    if print:
        click.echo(
            "Removed {} outlier snapshots.".format(len(acc_data) - len(acc_clean))
        )
    return acc_clean


def graph_account_balances(account_snapshots: List[Snapshot], graph: bool) -> None:
    """
    plot each account across the git hitsory
    """

    # clean data
    acc_clean: SnapshotData = remove_outliers(account_snapshots)

    plt.style.use("dark_background")
    # graph each data point
    fig, ax = plt.subplots(figsize=(18, 10))

    # get all account names
    account_names: Set[str] = set(
        chain(*[list(a[0]["account"].values) for a in acc_clean])
    )
    # create empty account data arrays for each timestamp
    account_history: Dict[str, NDFloatArr] = {
        n: np.zeros(len(acc_clean)) for n in account_names
    }

    secs: NDFloatArr = np.array([fix_timestamp(sn[1]) for sn in acc_clean])
    for i, sn in enumerate(acc_clean):
        ad: pd.DataFrame = sn[0]

        # loop over rows and add to account_history, to create 'line graphs' for each item
        for _, row in ad.iterrows():
            account_history[row["account"]][i] = row["current"]

    for acc, acc_list in account_history.items():
        ax.plot(secs, acc_list, label=acc)

    ax.xaxis.set_major_formatter(mdate.DateFormatter("%Y-%m-%d %H:%M:%S"))
    ax.yaxis.set_major_formatter(tick.StrMethodFormatter("${x:,}"))
    fig.autofmt_xdate()

    plt.legend(loc="upper left")
    plt.xlabel("Date")
    plt.ylabel("Account Balance")

    to_file = "/tmp/balance_history.png"
    plt.savefig(to_file)
    click.echo("Saved to {}".format(to_file))

    if graph:
        plt.show()
