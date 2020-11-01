# use the git history on the repo
# to return snapshots of data
# for my accounts at different times

import io
import csv
from pathlib import Path
from datetime import datetime

from dataclasses import dataclass
from typing import Optional, List, Iterator, Set, Iterable, Tuple

import git  # type: ignore[import]
from more_itertools import strip


@dataclass
class Account:
    institution: str  # company
    account: str  # sub-account with company, if applicable
    account_type: str  # checking/brokerage/savings
    current: float  # money in account/balance
    available: Optional[float]  # how much available on limit
    limit: Optional[float]  # possibly, how much limit is on card
    currency: str  # probably USD

    def __hash__(self) -> int:
        return hash(self.institution + self.account_type + str(self.current))


@dataclass
class Snapshot:
    accounts: List[Account]
    at: datetime


def parse_float_or_zero(s: str) -> float:
    try:
        return float(s.strip())
    except ValueError:
        return 0


BALANCES = "balances.csv"
# manually logged accounts/cash on hand, using budget.manual
MANUAL_BALANCES = "manual_balances.csv"


def get_accounts_at_commit(commit: git.Commit, filename: str) -> Iterator[Account]:
    try:
        blob = commit.tree / filename
    except KeyError:
        return
    with io.BytesIO(blob.data_stream.read()) as f:
        balances_str: str = f.read().decode("utf-8")
    bcsv = csv.reader(io.StringIO(balances_str))
    next(bcsv)  # ignore header row
    for r in bcsv:
        assert r[6] is not None
        yield Account(
            institution=r[0],
            account=r[1].strip(),
            account_type=r[2],
            current=float(r[3]),
            available=parse_float_or_zero(r[4]),
            limit=parse_float_or_zero(r[5]),
            currency="USD" if not bool(r[6].strip()) else r[6],
        )


def get_contents_at_commit(commit: git.Commit) -> Optional[Snapshot]:
    account_data: List[Account] = []
    # read the balance/manual balance files for this snapshot
    for bfile in (BALANCES, MANUAL_BALANCES):
        for acc in get_accounts_at_commit(commit, bfile):
            account_data.append(acc)
    if len(account_data) == 0:
        return None
    return Snapshot(accounts=account_data, at=commit.authored_datetime)


def unique_snapshots(snapshots: Iterable[Snapshot]) -> Iterator[Snapshot]:
    # remove snapshots which have the same account data but at different times
    emitted: Set[Tuple[Account, ...]] = set()
    for snap in sorted(snapshots, key=lambda s: s.at):
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
        strip(map(get_contents_at_commit, repo.iter_commits()), lambda s: s is None)  # type: ignore
    )
