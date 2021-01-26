import os

from pathlib import Path
from typing import Tuple, List, Optional

from .log import logger
from .load.transactions import (
    Transaction,
    read_transactions,
    remove_duplicate_transactions,
)
from .load.balances import generate_account_history, Snapshot

from .cleandata.accounts.fix_account_names import clean_data  # type: ignore
from .cleandata.transactions.transform import transform_all as transform  # type: ignore
from .cleandata.transactions.meta_categories import META_CATEGORIES  # type: ignore


def get_data_dir() -> Path:
    if "MINT_DATA" in os.environ:
        return Path(os.environ["MINT_DATA"])
    else:
        raise RuntimeError("No MINT_DATA environment variable!")


def data(
    ddir: Optional[Path] = None, debug: bool = False
) -> Tuple[List[Snapshot], List[Transaction]]:

    if ddir is None:
        ddir = get_data_dir()

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
            logger.warning(
                "Couldn't find meta_category for {}: {}".format(tr.category, tr)
            )

    # debug duplicates
    transactions = list(remove_duplicate_transactions(transactions, debug=debug))

    return balance_snapshots, transactions
