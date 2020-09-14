from functools import lru_cache
from typing import Iterator, List, Optional

from . import Matcher, Transaction, desc

try:
    # create a file called ./maps_conf.py
    # which has custom_maps to convert transactions
    from .maps_conf import custom_maps
except ImportError:
    custom_maps = lambda: []


# return multiple functions
# returns (predicate result, function that edits transaction)
def default_maps() -> Iterator[Matcher]:
    yield lambda t: (
        "starbucks" in desc(t),
        lambda: (
            setattr(t, "name", "Starbucks"),
            setattr(t, "category", "Coffee Shops"),
            t,
        ),
    )
    yield lambda t: (
        desc(t).startswith("lyft"),
        lambda: (setattr(t, "name", "Lyft"), setattr(t, "category", "Travel"), t),
    )
    yield lambda t: (desc(t) == "uber", lambda: (setattr(t, "category", "Travel"), t))
    yield lambda t: (
        "amazon prime" in desc(t),
        lambda: (
            setattr(t, "name", "Amazon Prime"),
            setattr(t, "category", "Subscriptions"),
            t,
        ),
    )
    yield lambda t: (
        "dreamhost" in desc(t),
        lambda: (setattr(t, "category", "Technology"), t),
    )
    yield lambda t: (
        "fandango" in desc(t),
        lambda: (
            setattr(t, "name", "Fandango"),
            setattr(t, "category", "Entertainment"),
            t,
        ),
    )
    yield lambda t: (
        "vultr" in desc(t),
        lambda: (setattr(t, "name", "Vultr"), setattr(t, "category", "Technology"), t),
    )
    yield lambda t: (
        "scaleway" in desc(t),
        lambda: (
            setattr(t, "name", "Scaleway"),
            setattr(t, "category", "Technology"),
            t,
        ),
    )
    yield lambda t: (
        "amazon" in desc(t) or "amzn mktp" in desc(t),
        lambda: (setattr(t, "name", "Amazon"), setattr(t, "category", "Shopping"), t),
    )
    yield lambda t: (
        "doordash" in desc(t),
        lambda: (
            setattr(t, "name", "DoorDash"),
            setattr(t, "category", "Food Dining"),
            t,
        ),
    )
    yield lambda t: (
        "jack in the box" in desc(t),
        lambda: (
            setattr(t, "name", "Jack in the Box"),
            setattr(t, "category", "Fast Food"),
            t,
        ),
    )
    yield lambda t: (
        "carl's jr." in desc(t),
        lambda: (
            setattr(t, "name", "Carls Jr"),
            setattr(t, "category", "Fast Food"),
            t,
        ),
    )
    yield lambda t: (
        "mcdonalds" in desc(t).replace("'", ''),
        lambda: (
            setattr(t, "name", "McDonalds"),
            setattr(t, "category", "Fast Food"),
            t,
        ),
    )
    yield lambda t: (
        desc(t).replace("'", '').startswith('dennys'),
        lambda: (
            setattr(t, "name", "Denny's"),
            setattr(t, "category", "Fast Food"),
            t,
        ),
    )
    yield lambda t: (
        "subway" in desc(t),
        lambda: (
            setattr(t, "name", "Subway"),
            setattr(t, "category", "Fast Food"),
            t,
        ),
    )
    yield lambda t: (
        "walgreen" in desc(t),
        lambda: (
            setattr(t, "name", "Walgreens"),
            setattr(t, "category", "Pharmacy"),
            t,
        ),
    )
    yield lambda t: (
        "peets" in desc(t),
        lambda: (
            setattr(t, "name", "Peets Coffee"),
            setattr(t, "category", "Coffee Shops"),
            t,
        ),
    )
    yield lambda t: (
        t.category == "Supermarkets",
        lambda: (
            setattr(t, "category", "Groceries"),
            t,
        ),
    )
    yield lambda t: (
        "safeway" in desc(t),
        lambda: (
            setattr(t, "name", "Safeway"),
            t,
        ),
    )
    yield lambda t: (
        "namecheap" in desc(t),
        lambda: (
            setattr(t, "name", "NameCheap"),
            setattr(t, "category", "Technology"),
            t,
        ),
    )
    yield lambda t: (
        "github.com" in desc(t),
        lambda: (
            setattr(t, "name", "Github Pro"),
            setattr(t, "category", "Subscriptions"),
            t,
        ),
    )


@lru_cache(1)
def maps() -> List[Matcher]:
    # get custom maps, then defaults
    def maps_gen() -> Iterator[Matcher]:
        yield from custom_maps()
        yield from default_maps()

    return list(maps_gen())


# handles a single transaction, calls every lambda against it
# in order (custom maps first, then defualt maps)
def transform_single(transact: Transaction) -> Optional[Transaction]:
    tr = transact
    for m in maps():
        # try with this pattern
        resp, tr_func = m(tr)
        if resp:
            tr = tr_func()[-1]
        if tr is None:
            return None
    return tr  # return unedited transaction if none matched


# handles all transactions, discards None
def transform_all(transactions: List[Transaction]) -> Iterator[Transaction]:
    yield from filter(lambda r: r is not None, map(transform_single, transactions))
