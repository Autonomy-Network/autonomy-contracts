from consts import *


# Test with and without sending eth with the tx




def test_newRequest(asc, mockTarget):
    # assert mockTarget.x() == 0

    print(asc.ALICE.balance())
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRequest(mockTarget, callData, asc.DENICE, asc.FR_ALICE)
    print(tx.events)
    print(tx.internal_transfers)
    print(tx.new_contracts)
    print(asc.ALICE.balance())

    assert asc.r.getNumRequests() == 1
    # assert asc.r.getRequest(0) == (asc.ALICE, mockTarget, )

    assert False