# use the git history on the repo
# to return snapshots of data
# for my accounts at different times

import io
import csv
from pathlib import Path
from datetime import datetime

from dataclasses import dataclass
from typing import NamedTuple, Optional, List, Iterator, Type, Any, Set, Iterable

import git
from more_itertools import strip


@dataclass
class Account:
    institution: str  # company
    account: Optional[str]  # sub-account with company, if applicable
    account_type: str  # checking/brokerage/savings
    current: float  # money in account/balance
    available: Optional[float]  # how much available on limit
    limit: Optional[float]  # possibly, how much limit is on card
    currency: str  # probably USD

    def __hash__(self) -> int:
        return hash(self.institution + self.account_type + str(self.current))


class Snapshot(NamedTuple):
    accounts: List[Account]
    at: datetime


def none_if_empty(s: str, to_type: Type = str) -> Optional[Any]:
    ss = s.strip()
    if ss == "":
        return None
    else:
        return to_type(ss)


BALANCES = "balances.csv"


def get_contents_at_commit(commit: git.Commit) -> Optional[Snapshot]:
    try:
        blob = commit.tree / BALANCES
    except KeyError:
        return None
    account_data: List[Account] = []
    with io.BytesIO(blob.data_stream.read()) as f:
        balances_str = f.read().decode("utf-8")
    buffer = io.StringIO(balances_str)
    bcsv = csv.reader(buffer)
    next(bcsv)  # ignore header row
    for r in bcsv:
        account_data.append(
            Account(
                institution=r[0],
                account=none_if_empty(r[1]),
                account_type=r[2],
                current=float(r[3]),
                available=none_if_empty(r[4], float),
                limit=none_if_empty(r[5], float),
                currency="USD" if r[6] is None else r[6],
            )
        )
    return Snapshot(accounts=account_data, at=commit.authored_datetime)


def unique_snapshots(snapshots: Iterable[Snapshot]) -> Iterator[Account]:
    # remove snapshots which have the same account data but at different times
    emitted: Set[Tuple[Account]] = set()
    for snap in snapshots:
        key = tuple(snap.accounts)
        if key not in emitted:
            emitted.add(key)
            yield snap
        else:
            pass
            # print("ignoring {}".format(snap))


def generate_account_history(ddir: Path) -> Iterator[Snapshot]:
    repo = git.Repo(str(ddir))
    yield from unique_snapshots(
        strip(map(get_contents_at_commit, repo.iter_commits()), lambda s: s is None)
    )
