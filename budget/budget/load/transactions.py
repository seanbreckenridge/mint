import os
import csv
import io
from itertools import chain
from math import modf
from datetime import date, timedelta
from pathlib import Path
from typing import List, Iterator, Optional, Dict, TextIO
from collections import defaultdict
from dataclasses import dataclass

import textdistance  # type: ignore[import]
from more_itertools import always_reversible
import git  # type: ignore[import]

from ..log import logger


# if anything is above this and it fuzzy matches the basics, should mark it as a duplicate
TRANSACTION_DUPLICATE_LIMIT = 100

# so that this can be used in lru_cache while cleaning transactions
@dataclass(unsafe_hash=True)
class Transaction:
    on: date
    amount: float  # positive is spending, negative is gaining/deposit
    name: str  # name of transaction/company
    account: str  # name of account this is related to
    category: str  # food, transfer, insurance
    meta_category: Optional[str] = None

    def fuzz_equals(self, other: "Transaction") -> bool:
        # dont use date since date may change as transactions are approved/metadata changes
        # name often changes again
        #
        basics_match: bool = (
            self.amount == other.amount
            and self.account.casefold() == other.account.casefold()
        )
        if not basics_match:
            return False
        decimal_part, integer_part = modf(self.amount)
        # if this isn't something like 10.0, 15.0, 20.0, more likely for it to be unique
        if not (decimal_part == 0.0 and integer_part % 5 != 0):
            return True
        return basics_match

    @classmethod
    def from_csv_row(cls, td: List[str]) -> "Transaction":
        return cls(
            on=date(**dict(zip(("year", "month", "day"), map(int, td[0].split("-"))))),
            amount=float(td[1]),
            name=td[2],
            account=td[3],
            category=td[4],
        )

    def fuzz_text(self, other: "Transaction") -> bool:
        t = self.name.casefold()
        o = other.name.casefold()
        for left, right in ((t, o), (t.replace(" ", ""), o.replace(" ", ""))):
            # if pure overlap
            if textdistance.algorithms.overlap(left, right) == 1.0:
                return True
            # if matched more than 80% of text or its over 10  chars
            overlap_str = textdistance.algorithms.lcsseq(left, right)
            if (
                len(overlap_str) > 0.8 * min(len(left), len(right))
                or len(overlap_str) > 8
            ):
                return True
        return False


TRANSACTION_FILE = "transactions.csv"

STATIC_TRANSACTION_FILES = [
    "old_transactions.csv",
    "manual_transactions.csv",
]


def _debug_textdistance(one: Transaction, two: Transaction) -> None:
    o = one.name.casefold()
    t = two.name.casefold()
    print("hamming", textdistance.algorithms.hamming(o, t))
    print("jaccard", textdistance.algorithms.jaccard(o, t))
    print("overlap", textdistance.algorithms.overlap(o, t))  ###
    print("bag", textdistance.algorithms.bag(o, t))
    print("lccseq", textdistance.algorithms.lcsseq(o, t))
    print("lccstr", textdistance.algorithms.lcsstr(o, t))
    print("ratcliff", textdistance.algorithms.ratcliff_obershelp(o, t))


def read_transaction_obj(file_obj: TextIO) -> Iterator[List[str]]:
    cr = csv.reader(io.StringIO(file_obj.read()))
    next(cr)  # ignore headers
    yield from cr


def read_transactions_at_commit(commit: git.objects.Commit) -> Iterator[Transaction]:
    try:
        blob = commit.tree / TRANSACTION_FILE
    except KeyError:
        return
    with io.BytesIO(blob.data_stream.read()) as f:
        transactions_str: str = f.read().decode("utf-8")
    # add each line from this commit to the set
    # convert to tuple so its hashable
    for line in read_transaction_obj(io.StringIO(transactions_str)):  # type: ignore[arg-type]
        yield Transaction.from_csv_row(line)


TEMP_TRANSACTION_NAMES = {"credit", "debit"}

# places where I might have transactions everyday, so don't fuzz match
# by checking days nearby
FORCE_EXACT = set([
    t.strip().casefold()
    for t in os.environ.get("BUDGET_FORCE_EXACT_DAY", "").split(",")
    if t.strip()
])


def _match_duplicate(
    all_transactions: Dict[date, List[Transaction]], new_transaction: Transaction
) -> Optional[Transaction]:
    """
    Returns a transaction if it matched by using a couple strategies
    """
    # try days close to this to remove duplicate transactions
    day_range = list(range(-3, 3))
    if new_transaction.name.casefold().strip() in FORCE_EXACT:
        day_range = [0]
    for k in [new_transaction.on + timedelta(days=r) for r in day_range]:
        for tr in all_transactions.get(k, []):
            # exact match
            # this still removes duplcate transactions on the same day from
            # which have the same name/cost/card -- is annoying to solve
            # probably need to move it up to read_transactions_history and
            # keep track of how many seemingly unique transactions exist
            # in a single snapshot, and then make sure those also exist in the result
            if tr == new_transaction:
                return tr
            # base fuzz matches, then try more specific matches
            if tr.fuzz_equals(new_transaction):
                # if this is 'CREDIT' or 'DEBIT'
                names = {n.casefold() for n in (tr.name, new_transaction.name)}
                if any((n in names for n in TEMP_TRANSACTION_NAMES)):
                    return tr
                if tr.fuzz_text(new_transaction):
                    return tr
                # probably a duplicate transaction if its that much?
                if tr.amount > TRANSACTION_DUPLICATE_LIMIT:
                    return tr
    return None


# read the transactions.csv history and return unique transactions
def read_transactions_history(repo: git.Repo) -> Iterator[Transaction]:
    all_transactions: Dict[date, List[Transaction]] = defaultdict(list)
    for commit in always_reversible(repo.iter_commits()):
        comm_transactions = list(read_transactions_at_commit(commit))
        for tr in comm_transactions:
            matched = _match_duplicate(all_transactions, tr)
            if matched is None:
                all_transactions[tr.on].append(tr)
            else:
                pass
                # ~170,000 logs, so not worth logging here
                # logger.debug(f"Matched duplicate:\n{tr}\n{matched}")

    # destructure defaultdict
    sorted_transactions = list(chain(*(v for v in all_transactions.values())))
    yield from sorted(sorted_transactions, key=lambda t: t.on)


def read_transactions(ddir: Path) -> Iterator[Transaction]:
    # should just read from the current static files, I edit these manually
    for tfile in STATIC_TRANSACTION_FILES:
        full_tfile = ddir / tfile
        if full_tfile.exists():
            with full_tfile.open(newline="") as tr:
                yield from map(Transaction.from_csv_row, read_transaction_obj(tr))
        else:
            logger.warning(
                "File at {} doesn't exist, ignoring...".format(str(full_tfile))
            )
    yield from read_transactions_history(git.Repo(str(ddir)))
