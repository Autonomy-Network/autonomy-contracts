from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Test with and without sending eth with the tx


def test_newRawRequest_no_eth(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, False, False, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, False, False, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0
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

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL


def test_newRawRequest_pay_with_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, False, True, 0, asc.DENICE, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0
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

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool')
)
def test_newRawRequest_with_eth_and_pay_ASCoin(asc, mockTarget, ethForCall, payWithASC):
    msgValue = ethForCall
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawRequest(mockTarget, callData, False, payWithASC, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})

    request = (asc.BOB.address, mockTarget.address, callData, False, payWithASC, msgValue, ethForCall, asc.DENICE.address)
    # Should've changed
    assert asc.r.getRawRequests() == [request]
    assert asc.r.getRawRequestsLen() == 1
    assert asc.r.getRawRequest(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0
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

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_newRawRequest_verifySender(asc, mockTarget, ethForCall, payWithASC, userAddr, sender):
    assert mockTarget.userAddr() == ADDR_0
    msgValue = ethForCall
    callData = mockTarget.setAddrPayVerified.encode_input(userAddr)

    if userAddr != sender:
        with reverts(REV_MSG_CALLDATA_NOT_VER):
            asc.r.newRawRequest(mockTarget, callData, True, False, ethForCall, asc.DENICE, {'from': sender, 'value': msgValue})
    else:
        tx = asc.r.newRawRequest(mockTarget, callData, True, True, ethForCall, asc.DENICE, {'from': sender, 'value': msgValue})

        request = (sender.address, mockTarget.address, callData, True, True, ethForCall, ethForCall, asc.DENICE.address)
        # Should've changed
        assert asc.r.getRawRequests() == [request]
        assert asc.r.getRawRequestsLen() == 1
        assert asc.r.getRawRequest(0) == request
        assert tx.events["RawReqAdded"][0].values() == [0]
        assert sender.balance() == INIT_ETH_BAL - msgValue
        assert asc.r.balance() == msgValue

        # Shouldn't've changed
        assert mockTarget.x() == 0
        assert mockTarget.userAddr() == ADDR_0
        assert mockTarget.msgSender() == ADDR_0
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

        assert mockTarget.balance() == 0

        assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
        assert asc.ASC.balanceOf(asc.DENICE) == 0
        assert asc.ASC.balanceOf(mockTarget) == 0
        assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL


def test_newRawRequest_rev_target_empty(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NZ_ADDR):
        asc.r.newRawRequest(ADDR_0, callData, False, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRawRequest_rev_target_is_registry(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        asc.r.newRawRequest(asc.r, callData, False, False, 0, asc.DENICE, asc.FR_BOB)


def test_newRawRequest_rev_target_is_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        asc.r.newRawRequest(asc.ASC, callData, False, False, 0, asc.DENICE, asc.FR_BOB)


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawRequest_rev_validEth_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall != msgValue:
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            asc.r.newRawRequest(mockTarget, callData, False, True, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawRequest_rev_validEth_no_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall > msgValue:
        with reverts(REV_MSG_ETHFORCALL_HIGH):
            asc.r.newRawRequest(mockTarget, callData, False, False, ethForCall, asc.DENICE, {'from': asc.BOB, 'value': msgValue})


def test_newRawRequest_rev_verifySender_calldata_invalid(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_CALLDATA_NOT_VER):
        asc.r.newRawRequest(mockTarget, callData, True, False, 0, asc.DENICE, asc.FR_BOB)