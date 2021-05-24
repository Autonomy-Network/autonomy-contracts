from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Test with and without sending eth with the tx


def test_newRawReq_no_eth(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawReq(mockTarget, asc.DENICE, callData, 0, False, False, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, False)
    # Should've changed
    reqs = [request]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 1
    assert asc.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, 1)
    assert asc.r.getHashedReqsSlice(0, 0) == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)
    
    assert asc.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, 1)
    assert asc.r.getHashedReqsUnveriSlice(0, 0) == []
    assert asc.r.getHashedReqsUnveriLen() == 0
    with reverts():
        asc.r.getHashedReqUnveri(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_newRawReq_pay_with_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawReq(mockTarget, asc.DENICE, callData, 0, False, True, asc.FR_BOB)

    request = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    # Should've changed
    reqs = [request]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 1
    assert asc.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, 1)
    assert asc.r.getHashedReqsSlice(0, 0) == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)
    
    assert asc.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, 1)
    assert asc.r.getHashedReqsUnveriSlice(0, 0) == []
    assert asc.r.getHashedReqsUnveriLen() == 0
    with reverts():
        asc.r.getHashedReqUnveri(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool')
)
def test_newRawReq_with_eth_and_pay_ASCoin(asc, mockTarget, ethForCall, payWithASC):
    msgValue = ethForCall
    callData = mockTarget.setX.encode_input(5)
    tx = asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, payWithASC, {'from': asc.BOB, 'value': msgValue})

    request = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, False, payWithASC)
    # Should've changed
    reqs = [request]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 1
    assert asc.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, 1)
    assert asc.r.getHashedReqsSlice(0, 0) == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)
    
    assert asc.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, 1)
    assert asc.r.getHashedReqsUnveriSlice(0, 0) == []
    assert asc.r.getHashedReqsUnveriLen() == 0
    with reverts():
        asc.r.getHashedReqUnveri(0)

    assert asc.BOB.balance() == INIT_ETH_BAL - msgValue
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == msgValue

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_newRawReq_verifySender(asc, mockTarget, ethForCall, payWithASC, userAddr, sender):
    assert mockTarget.userAddr() == ADDR_0
    msgValue = ethForCall
    callData = mockTarget.setAddrPayVerified.encode_input(userAddr)

    if userAddr != sender:
        with reverts(REV_MSG_CALLDATA_NOT_VER):
            asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, True, payWithASC, {'from': sender, 'value': msgValue})
    else:
        tx = asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, True, payWithASC, {'from': sender, 'value': msgValue})

        request = (sender.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, True, payWithASC)
        # Should've changed
        reqs = [request]
        assert asc.r.getRawReqs() == reqs
        # Should revert when using indexes above the length
        with reverts():
            asc.r.getRawReqsSlice(0, len(reqs) + 1)
        assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
        assert asc.r.getRawReqLen() == 1
        assert asc.r.getRawReq(0) == request
        assert tx.events["RawReqAdded"][0].values() == [0]
        assert sender.balance() == INIT_ETH_BAL - msgValue
        assert asc.r.balance() == msgValue

        # Shouldn't've changed
        assert mockTarget.x() == 0
        assert mockTarget.userAddr() == ADDR_0
        assert mockTarget.msgSender() == ADDR_0
        
        assert asc.r.getHashedReqs() == []
        # Should revert when using indexes above the length
        with reverts():
            asc.r.getHashedReqsSlice(0, 1)
        assert asc.r.getHashedReqsSlice(0, 0) == []
        assert asc.r.getHashedReqsLen() == 0
        with reverts():
            asc.r.getHashedReq(0)
        
        assert asc.r.getHashedReqsUnveri() == []
        # Should revert when using indexes above the length
        with reverts():
            asc.r.getHashedReqsUnveriSlice(0, 1)
        assert asc.r.getHashedReqsUnveriSlice(0, 0) == []
        assert asc.r.getHashedReqsUnveriLen() == 0
        with reverts():
            asc.r.getHashedReqUnveri(0)

        assert mockTarget.balance() == 0

        assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
        assert asc.ASC.balanceOf(asc.DENICE) == 0
        assert asc.ASC.balanceOf(mockTarget) == 0
        assert asc.ASC.balanceOf(asc.r) == 0

        assert asc.r.getReqCountOf(asc.BOB) == 0
        assert asc.r.getExecCountOf(asc.ALICE) == 0
        assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_newRawReq_rev_target_empty(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NZ_ADDR):
        asc.r.newRawReq(ADDR_0, asc.DENICE, callData, 0, False, False, asc.FR_BOB)


def test_newRawReq_rev_target_is_registry(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        asc.r.newRawReq(asc.r, asc.DENICE, callData, 0, False, False, asc.FR_BOB)


def test_newRawReq_rev_target_is_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        asc.r.newRawReq(asc.ASC, asc.DENICE, callData, 0, False, False, asc.FR_BOB)


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawReq_rev_validEth_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall != msgValue:
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, True, {'from': asc.BOB, 'value': msgValue})


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawReq_rev_validEth_no_payWithASC(asc, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall > msgValue:
        with reverts(REV_MSG_ETHFORCALL_HIGH):
            asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, False, {'from': asc.BOB, 'value': msgValue})


def test_newRawReq_rev_verifySender_calldata_invalid(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_CALLDATA_NOT_VER):
        asc.r.newRawReq(mockTarget, asc.DENICE, callData, 0, True, False, asc.FR_BOB)