from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Test with and without sending eth with the tx


def test_newRawReq_no_eth(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, False, auto.FR_BOB)

    request = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False)
    # Should've changed
    reqs = [request]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 1
    assert auto.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsSlice(0, 0) == []
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)
    
    assert auto.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, 1)
    assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
    assert auto.r.getHashedReqsUnveriLen() == 0
    with reverts():
        auto.r.getHashedReqUnveri(0)

    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert auto.r.balance() == 0

    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_newRawReq_pay_with_AUTO(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    tx = auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, True, auto.FR_BOB)

    request = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, True)
    # Should've changed
    reqs = [request]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 1
    assert auto.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsSlice(0, 0) == []
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)
    
    assert auto.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, 1)
    assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
    assert auto.r.getHashedReqsUnveriLen() == 0
    with reverts():
        auto.r.getHashedReqUnveri(0)

    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert auto.r.balance() == 0

    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithAUTO=strategy('bool')
)
def test_newRawReq_with_eth_and_pay_AUTO(auto, mockTarget, ethForCall, payWithAUTO):
    msgValue = ethForCall
    callData = mockTarget.setX.encode_input(5)
    tx = auto.r.newRawReq(mockTarget, auto.DENICE, callData, ethForCall, False, payWithAUTO, {'from': auto.BOB, 'value': msgValue})

    request = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, payWithAUTO)
    # Should've changed
    reqs = [request]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 1
    assert auto.r.getRawReq(0) == request
    assert tx.events["RawReqAdded"][0].values() == [0]
    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsSlice(0, 0) == []
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)
    
    assert auto.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, 1)
    assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
    assert auto.r.getHashedReqsUnveriLen() == 0
    with reverts():
        auto.r.getHashedReqUnveri(0)

    assert auto.BOB.balance() == INIT_ETH_BAL - msgValue
    assert auto.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert auto.r.balance() == msgValue

    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithAUTO=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_newRawReq_verifySender(auto, mockTarget, ethForCall, payWithAUTO, userAddr, sender):
    assert mockTarget.userAddr() == ADDR_0
    msgValue = ethForCall
    callData = mockTarget.setAddrPayVerified.encode_input(userAddr)

    if userAddr != sender:
        with reverts(REV_MSG_CALLDATA_NOT_VER):
            auto.r.newRawReq(mockTarget, auto.DENICE, callData, ethForCall, True, payWithAUTO, {'from': sender, 'value': msgValue})
    else:
        tx = auto.r.newRawReq(mockTarget, auto.DENICE, callData, ethForCall, True, payWithAUTO, {'from': sender, 'value': msgValue})

        request = (sender.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, True, payWithAUTO)
        # Should've changed
        reqs = [request]
        assert auto.r.getRawReqs() == reqs
        # Should revert when using indexes above the length
        with reverts():
            auto.r.getRawReqsSlice(0, len(reqs) + 1)
        assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
        assert auto.r.getRawReqLen() == 1
        assert auto.r.getRawReq(0) == request
        assert tx.events["RawReqAdded"][0].values() == [0]
        assert sender.balance() == INIT_ETH_BAL - msgValue
        assert auto.r.balance() == msgValue

        # Shouldn't've changed
        assert mockTarget.x() == 0
        assert mockTarget.userAddr() == ADDR_0
        assert mockTarget.msgSender() == ADDR_0
        
        assert auto.r.getHashedReqs() == []
        # Should revert when using indexes above the length
        with reverts():
            auto.r.getHashedReqsSlice(0, 1)
        assert auto.r.getHashedReqsSlice(0, 0) == []
        assert auto.r.getHashedReqsLen() == 0
        with reverts():
            auto.r.getHashedReq(0)
        
        assert auto.r.getHashedReqsUnveri() == []
        # Should revert when using indexes above the length
        with reverts():
            auto.r.getHashedReqsUnveriSlice(0, 1)
        assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
        assert auto.r.getHashedReqsUnveriLen() == 0
        with reverts():
            auto.r.getHashedReqUnveri(0)

        assert mockTarget.balance() == 0

        assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
        assert auto.AUTO.balanceOf(auto.DENICE) == 0
        assert auto.AUTO.balanceOf(mockTarget) == 0
        assert auto.AUTO.balanceOf(auto.r) == 0

        assert auto.r.getReqCountOf(auto.BOB) == 0
        assert auto.r.getExecCountOf(auto.ALICE) == 0
        assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_newRawReq_rev_target_empty(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NZ_ADDR):
        auto.r.newRawReq(ADDR_0, auto.DENICE, callData, 0, False, False, auto.FR_BOB)


def test_newRawReq_rev_target_is_registry(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        auto.r.newRawReq(auto.r, auto.DENICE, callData, 0, False, False, auto.FR_BOB)


def test_newRawReq_rev_target_is_AUTO(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        auto.r.newRawReq(auto.AUTO, auto.DENICE, callData, 0, False, False, auto.FR_BOB)


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawReq_rev_validEth_payWithAUTO(auto, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall != msgValue:
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            auto.r.newRawReq(mockTarget, auto.DENICE, callData, ethForCall, False, True, {'from': auto.BOB, 'value': msgValue})


@given(
    ethForCall=strategy('uint256', max_value=INIT_ETH_BAL),
    msgValue=strategy('uint256', max_value=INIT_ETH_BAL)
)
def test_newRawReq_rev_validEth_no_payWithAUTO(auto, mockTarget, ethForCall, msgValue):
    callData = mockTarget.setX.encode_input(5)
    if ethForCall > msgValue:
        with reverts(REV_MSG_ETHFORCALL_HIGH):
            auto.r.newRawReq(mockTarget, auto.DENICE, callData, ethForCall, False, False, {'from': auto.BOB, 'value': msgValue})


def test_newRawReq_rev_verifySender_calldata_invalid(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_CALLDATA_NOT_VER):
        auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, True, False, auto.FR_BOB)