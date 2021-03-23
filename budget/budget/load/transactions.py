import sys
import csv
import io
from datetime import date
from pathlib import Path
from typing import List, Iterator, Optional, Set, Tuple, Sequence
from dataclasses import dataclass

import git  # type: ignore[import]

from ..log import logger


@dataclass
class Transaction:
    on: date
    amount: float  # positive is spending, negative is gaining/deposit
    name: str  # name of transaction/company
    account: str  # name of account this is related to
    category: str  # food, transfer, insurance
    meta_category: Optional[str] = None


TRANSACTION_FILE = "transactions.csv"

STATIC_TRANSACTION_FILES = [
    "old_transactions.csv",
    "manual_transactions.csv",
]


def read_transaction_obj(file_obj: io.IOBase) -> Iterator[List[str]]:
    cr = csv.reader(file_obj)  # type: ignore
    next(cr)  # ignore headers
    yield from cr


# read the transactions.csv history and return unique transactions
def read_transactions_history(repo: git.Repo) -> Iterator[Transaction]:
    emitted_lines: Set[Tuple[str, ...]] = set()
    for commit in repo.iter_commits():
        try:
            blob = commit.tree / TRANSACTION_FILE
        except KeyError:
            continue
        with io.BytesIO(blob.data_stream.read()) as f:
            transactions_str: str = f.read().decode("utf-8")
        # add each line from this commit to the set
        # convert to tuple so its hashable
        for line in map(tuple, read_transaction_obj(io.StringIO(transactions_str))):  # type: ignore[arg-type]
            if line not in emitted_lines:
                emitted_lines.add(line)  # type: ignore
            else:
                logger.debug(
                    f"while parsing transactions git history: {line} already in set"
                )
    yield from map(parse_transaction, emitted_lines)


def read_transactions(ddir: Path) -> Iterator[Transaction]:
    for tfile in STATIC_TRANSACTION_FILES:
        full_tfile = ddir / tfile
        if full_tfile.exists():
            with full_tfile.open(newline="") as tr:
                yield from map(parse_transaction, read_transaction_obj(tr))  # type: ignore[arg-type]
        else:
            logger.warning(
                "File at {} doesn't exist, ignoring...".format(str(full_tfile))
            )
    yield from read_transactions_history(git.Repo(str(ddir)))


def parse_transaction(td: Sequence[str]) -> Transaction:
    return Transaction(
        on=date(**dict(zip(("year", "month", "day"), map(int, td[0].split("-"))))),
        amount=float(td[1]),
        name=td[2],
        account=td[3],
        category=td[4],
    )


def remove_duplicate_transactions(
    transactions: List[Transaction],
    debug: bool = False,
) -> Iterator[Transaction]:
    emitted: Set[Tuple[date, float]] = set()
    for tr in sorted(transactions, key=lambda t: t.on):
        # TODO: use dice coefficient on lowered transaction name?
        key = (tr.on, tr.amount)
        if key not in emitted:
            emitted.add(key)
            yield tr
        else:
            if debug:
                print("removing transaction {}".format(tr), file=sys.stderr)
