import csv
from datetime import date
from pathlib import Path
from typing import List, Iterator, Iterable
from dataclasses import dataclass


@dataclass
class Transaction:
    on: date
    amount: float  # positive is spending, negative is gaining/deposit
    name: str  # name of transaction/company
    account: str  # name of account this is related to
    category: str  # food, transfer, insurance


def read_transactions(ddir: Path) -> Iterator[Transaction]:
    with (ddir / "transactions.csv").open(newline="") as tr:
        cr = csv.reader(tr)
        next(cr)  # ignore headers
        for td in cr:
            yield parse_transaction(td)
    old_transactions = ddir / "old_transactions.csv"
    if old_transactions.exists():
        with old_transactions.open(newline="") as tr:
            cr = csv.reader(tr)
            next(cr)  # ignore headers
            for td in cr:
                yield parse_transaction(td)


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
