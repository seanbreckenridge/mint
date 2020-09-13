from typing import NamedTuple

# data cleaning to replace fields on accounts
class CleanAccount(NamedTuple):
    from_institution: str
    from_account: str
    from_account_type: str
    to_institution: str
    to_account: str
    to_account_type: str


"""
e.g: for bad account data from plaid:
CleanAccount(
from_institution='interest account',  # this isn't really representative
from_account=None,
from_account_type='savings',
to_institution='name of company',  # replace with what this actually is, so its readable
to_account='',
to_type='savings',
"""
