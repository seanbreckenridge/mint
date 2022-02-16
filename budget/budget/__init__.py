import os

from pathlib import Path
from typing import Tuple, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .load.transactions import Transaction
    from .load.balances import Snapshot


def get_data_dir() -> Path:
    if "MINT_DATA" in os.environ:
        return Path(os.environ["MINT_DATA"])
    else:
        raise RuntimeError("No MINT_DATA environment variable!")


def data(
    ddir: Optional[Path] = None, debug: bool = False
) -> Tuple[List["Snapshot"], List["Transaction"]]:
    import logging
    from .log import logger

    from .load.transactions import (
        read_transactions,
    )
    from .load.balances import generate_account_history

    from .cleandata.accounts.fix_account_names import clean_data
    from .cleandata.transactions.transform import transform_all as transform  # type: ignore[attr-defined]
    from .cleandata.transactions.meta_categories import META_CATEGORIES

    if debug:
        from .log import setup as log_setup

        log_setup(level=logging.DEBUG)

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
            logger.info(
                "Couldn't find meta_category for {}: {}".format(tr.category, tr)
            )

    return balance_snapshots, transactions
