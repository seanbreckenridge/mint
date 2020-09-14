import warnings

from pathlib import Path
from typing import Tuple, List

from .load.transactions import (
    Transaction,
    read_transactions,
)  # , debug_duplicate_transactions
from .load.balances import generate_account_history, Snapshot

from .cleandata.accounts.fix_account_names import clean_data
from .cleandata.transactions.transform import transform_all as transform
from .cleandata.transactions.meta_categories import META_CATEGORIES


def data(ddir: Path) -> Tuple[List[Snapshot], List[Transaction]]:

    # load in and clean data
    balance_snapshots, transactions = clean_data(
        list(generate_account_history(ddir)),
        list(read_transactions(ddir)),
    )

    # transform transaction description/categories
    transactions = list(transform(transactions))

    for tr in transactions:
        if tr.category in META_CATEGORIES:
            tr.meta_category = META_CATEGORIES[tr.category]
        else:
            warnings.warn(
                "Could not find a meta category for {} ({})".format(tr.category, tr)
            )

    # debug duplicates
    # transactions = list(debug_duplicate_transactions(transactions))

    return balance_snapshots, transactions
