"""
Cleans/Maps transaction information to a nicer format
"""

from typing import Callable, Tuple, Union, Iterable, Any
from functools import lru_cache
from ...load.transactions import Transaction

# this is a weird hack to allow multi-line-ish lambda expressions
# to handle predicates.
# The return type is a bool, and function that if you call, edits the transaction
# if bool is true, you should call the function, and that edits the dataclass
# the resulting value is in the last element of return value
# if that value is None, it means to ignore this transaction
EditTransaction = Callable[[], Iterable[Union[Any, Transaction]]]
PredicateHandler = Tuple[bool, EditTransaction]
Matcher = Callable[[Transaction], PredicateHandler]


@lru_cache(maxsize=None)
def desc(t: Transaction) -> str:
    return t.name.casefold()
