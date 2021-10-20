from consts import *
from brownie import AUTO, reverts
from brownie.test import given, strategy


@given(new_operator=strategy('address'))
def test_addDefaultOperators(a, freshAUTOToken, new_operator):
    assert freshAUTOToken.defaultOperators() == []

    freshAUTOToken.addDefaultOperators([new_operator])

    assert freshAUTOToken.defaultOperators() == [new_operator]

    amount = 10
    for addr in a:
        if addr == new_operator:
            freshAUTOToken.operatorSend(a[0], a[1], amount, "", "", {'from': addr})

            assert freshAUTOToken.balanceOf(a[1]) == amount
        # To ignore the 1st, which is an operator for itself
        elif addr != a[0]:
            with reverts(REV_MSG_NOT_OPERATOR):
                freshAUTOToken.operatorSend(a[0], a[1], amount, "", "", {'from': addr})