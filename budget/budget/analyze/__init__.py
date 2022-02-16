"""
Exposes this (pandas/analysis code) info importable from across the system
"""

from typing import List, Optional, Set, Iterator
from datetime import datetime

import pandas as pd  # type: ignore[import]

from .. import data
from ..load.balances import Snapshot
from ..load.transactions import Transaction
from .balance_history import remove_outliers, SnapshotData


def cleaned_snapshots(
    sorted_snapshots: Optional[List[Snapshot]] = None,
) -> Iterator[Snapshot]:
    snapshots: List[Snapshot] = []
    if sorted_snapshots is None:
        snapshots, _ = data()
        snapshots.sort(key=lambda s: s.at)
    else:
        snapshots = sorted_snapshots
    # uses code in ./balance_history.py to remove outliers
    df: SnapshotData = cleaned_snapshots_df(sorted_snapshots=snapshots)
    # timestamps of snapshots that werent removed by outliers
    use_datetimes: Set[datetime] = set([dt for _, dt in df])
    for sn in snapshots:
        if sn.at in use_datetimes:
            yield sn


def cleaned_snapshots_df(
    sorted_snapshots: Optional[List[Snapshot]] = None, debug: bool = False
) -> SnapshotData:
    snapshots: List[Snapshot] = []
    if sorted_snapshots is None:
        snapshots, _ = data(debug=debug)
        snapshots.sort(key=lambda s: s.at)
    else:
        snapshots = sorted_snapshots
    cleaned_acc: SnapshotData = remove_outliers(snapshots, print=debug)
    return cleaned_acc


def transactions_df(
    sorted_transactions: Optional[List[Transaction]] = None,
) -> pd.DataFrame:
    transactions: List[Transaction] = []
    if sorted_transactions is None:
        _, transactions = data()
        transactions.sort(key=lambda s: s.on)
    else:
        transactions = sorted_transactions
    return pd.DataFrame.from_dict(transactions)
