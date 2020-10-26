import warnings

from itertools import chain
from typing import Tuple, List, Dict, Set


from .model import CleanAccount
from ...load.balances import Account, Snapshot
from ...load.transactions import Transaction
from ...log import logger

try:
    # private configuration
    # default_account is just a string with matches the to_institution for an account. if CSV is missing account info,
    # or manual transactions don't have an account associated with it, it uses that (probably just my typical
    # checking account/cash)
    from .cleandata_conf import accounts_conf, default_account
except ImportError:
    warnings.warn("Could not import cleandata_conf.py")
    # no extra personal config, so just use defaults
    accounts_conf = lambda: []  # type: ignore[return-value, assignment]
    default_account: str = "<NO ACCOUNT>"  # type: ignore[no-redef]

# what clean_data uses to get CleanAccount information, to clean the data
# define a function in ./cleandata_conf.py called accounts_conf which
# returns an iterable of CleanAccount namedtuples, to fix the names of account/transactions
def get_configuration() -> List[CleanAccount]:
    return list(accounts_conf())


def clean_data(
    balances: List[Snapshot], transactions: List[Transaction]
) -> Tuple[List[Snapshot], List[Transaction]]:
    cleaners: List[CleanAccount] = get_configuration()
    # create O(1) access, use non-nullable fields
    cleaner_map: Dict[Tuple[str, str, str], CleanAccount] = {
        (cl.from_institution, cl.from_account, cl.from_account_type): cl
        for cl in cleaners
    }

    cleaned_balances: List[Snapshot] = []

    # clean data for accounts on accounts
    for snapshot in balances:
        cleaned_accounts = []
        for acc in snapshot.accounts:
            # if this should be replaced
            key = (acc.institution, acc.account, acc.account_type)
            if key in cleaner_map:
                cl: CleanAccount = cleaner_map[key]
                cleaned_accounts.append(
                    Account(
                        institution=cl.to_institution,  # replace metadata
                        account=cl.to_account,
                        account_type=cl.to_account_type,
                        current=acc.current,
                        available=acc.available,
                        limit=acc.limit,
                        currency=acc.currency,
                    )
                )
            else:
                cleaned_accounts.append(acc)
        cleaned_balances.append(Snapshot(at=snapshot.at, accounts=cleaned_accounts))

    # replace account names on transactions
    replace_account: Dict[str, str] = {
        cl.from_account: cl.to_account for cl in cleaners
    }
    for tr in transactions:
        assert tr.account is not None
        if tr.account in replace_account:
            tr.account = replace_account[tr.account]

    # validate data
    # get names of all the accounts, including any manual ones
    account_names: Set[str] = set(
        chain(*[[acc.account for acc in cl.accounts] for cl in cleaned_balances])  # type: ignore[arg-type]
    )
    # make sure every transaction is attached to an account
    # could just define a 'cash' institution if you wanted to keep track of money in wallet
    for tr in transactions:
        if tr.account not in account_names:
            logger.debug("Using default account name for {}...".format(tr))
            tr.account = default_account
            # warnings.warn(
            #    "Could not find balance information for {} (in {}) in accounts!: {}".format(
            #        tr.account, tr, account_names
            #    )
            # )
    return (cleaned_balances, transactions)
