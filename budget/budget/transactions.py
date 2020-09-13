import csv
from datetime import date
from pathlib import Path
from typing import List, Iterator
from dataclasses import dataclass


@dataclass
class Transaction:
    on: date
    amount: float
    name: str
    account: str
    category: str


def read_transactions(ddir: Path) -> Iterator[Transaction]:
    with (ddir / "transactions.csv").open() as tr:
        cr = csv.reader(tr)
        next(cr)  # ignore headers
        for td in cr:
            yield parse_transaction(td)
    old_transactions = ddir / "old_transactions.csv"
    if old_transactions.exists():
        # old_transactions file doesnt have a header, same format as regular transactions
        with old_transactions.open() as tr:
            cr = csv.reader(tr)
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
