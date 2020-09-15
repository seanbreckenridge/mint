import csv
from datetime import date, datetime
from pathlib import Path
from typing import List, Iterator, Iterable, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class Transaction:
    on: date
    amount: float  # positive is spending, negative is gaining/deposit
    name: str  # name of transaction/company
    account: str  # name of account this is related to
    category: str  # food, transfer, insurance
    meta_category: Optional[str] = None

TRANSACTION_FILES = ['transactions.csv', 'old_transactions.csv', 'manual_transactions.csv']

def read_transactions(ddir: Path) -> Iterator[Transaction]:
    for tfile in TRANSACTION_FILES:
        full_tfile = ddir / tfile
        if full_tfile.exists():
            with full_tfile.open(newline="") as tr:
                cr = csv.reader(tr)
                next(cr)  # ignore headers
                for td in cr:
                    yield parse_transaction(td)
        else:
            warnings.warn(f"{full_tfile} doesn't exist, ignoring...")


def parse_transaction(td: List[str]) -> Transaction:
    return Transaction(
        on=date(**dict(zip(("year", "month", "day"), map(int, td[0].split("-"))))),
        amount=float(td[1]),
        name=td[2],
        account=td[3],
        category=td[4],
    )


def debug_duplicate_transactions(
    transactions: Iterable[Transaction],
) -> Iterator[Transaction]:
    emitted: Set[Tuple[datetime, float, str]] = set()
    for tr in sorted(transactions, key=lambda t: t.on):
        key = (tr.on, tr.amount, tr.name)
        if key not in emitted:
            emitted.add(key)
            yield tr
        else:
            print("removing transaction {}".format(tr))
