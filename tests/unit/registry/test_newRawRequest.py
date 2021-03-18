from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Test with and without sending eth with the tx


def test_newRawRequest_no_eth(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, False, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, False, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD

    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)
    
    assert asc.r.getHashedIpfsReqsNoEth() == []
    assert asc.r.getHashedIpfsReqsNoEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqNoEth(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(mockTarget) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL


def test_newRawRequest_pay_with_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, True, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, True, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD

    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)
    
    assert asc.r.getHashedIpfsReqsNoEth() == []
    assert asc.r.getHashedIpfsReqsNoEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqNoEth(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(mockTarget) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool')
)
def test_newRawRequest_with_eth_and_pay_ASCoin(asc, mockTarget, ethForCall, payWithASC):
    msgValue = ethForCall
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, payWithASC, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})

    request = (asc.BOB.address, mockTarget.address, callData, payWithASC, msgValue, ethForCall, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD

    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)
    
    assert asc.r.getHashedIpfsReqsNoEth() == []
    assert asc.r.getHashedIpfsReqsNoEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqNoEth(0)

    assert asc.BOB.balance() == INIT_ETH_BAL - msgValue
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == msgValue

    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(mockTarget) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL


def test_newRawRequest_rev_target_empty(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NZ_ADDR):
        asc.r.newRawRequest(ADDR_0, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRawRequest_rev_target_is_registry(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET_REG):
        asc.r.newRawRequest(asc.r, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRawRequest_rev_target_is_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET_REG):
        asc.r.newRawRequest(asc.ASCoin, callData, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRawRequest_rev_callData(asc, mockTarget):
    with reverts(REV_MSG_NZ_BYTES):
        asc.r.newRawRequest(mockTarget, "", False, 0, asc.DENICE, asc.FR_BOB)


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawRequest_rev_validEth_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall != msgValue:
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            asc.r.newRawRequest(mockTarget, callData, True, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawRequest_rev_validEth_no_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall > msgValue:
        with reverts(REV_MSG_ETHFORCALL_HIGH):
            asc.r.newRawRequest(mockTarget, callData, False, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})