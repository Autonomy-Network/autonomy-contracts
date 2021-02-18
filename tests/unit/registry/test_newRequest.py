from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy



# Test with and without sending eth with the tx


def test_newRequest_no_eth(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRequest(mockTarget, callData, False, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, False, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRequests() == [request]
    assert asc.r.getRequestsLength() == 1
    assert asc.r.getRequest(0) == request
    assert tx.events["RequestAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_newRequest_pay_with_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRequest(mockTarget, callData, True, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, True, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRequests() == [request]
    assert asc.r.getRequestsLength() == 1
    assert asc.r.getRequest(0) == request
    assert tx.events["RequestAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


@given(
    ethForCall=strategy('uint256', max_value=int(E_18)),
    payWithASCoin=strategy('bool')
)
def test_newRequest_with_eth_and_pay_ASCoin(asc, mockTarget, ethForCall, payWithASCoin):
    msgValue = 2 * ethForCall
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRequest(mockTarget, callData, payWithASCoin, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})

    request = (asc.BOB.address, mockTarget.address, callData, payWithASCoin, msgValue, ethForCall, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRequests() == [request]
    assert asc.r.getRequestsLength() == 1
    assert asc.r.getRequest(0) == request
    assert tx.events["RequestAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_newRequest_rev_target_empty(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NZ_ADDR):
        asc.r.newRequest(ADDR_0, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRequest_rev_target_is_registry(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET_REG):
        asc.r.newRequest(asc.r, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRequest_rev_target_is_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET_REG):
        asc.r.newRequest(asc.ASCoin, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRequest_rev_callData(asc, mockTarget):
    with reverts(REV_MSG_NZ_BYTES):
        asc.r.newRequest(mockTarget, "", False, 0, asc.DENICE, asc.FR_BOB)