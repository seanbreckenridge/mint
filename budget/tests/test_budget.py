# just import stuff to make sure nothing is broken


def test_budget() -> None:
    import budget.load.balances
    import budget.load.transactions
    import budget.analyze

    assert True
