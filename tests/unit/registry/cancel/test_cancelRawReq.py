from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Making a request that calls executeRawReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call executeRawReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_cancelRawReq_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, True, {'from': auto.BOB})
    # Create request to be executed directly
    callData = mockReentrancyAttack.callCancelRawReq.encode_input(0)
    auto.r.newRawReq(mockReentrancyAttack, auto.DENICE, callData, 0, False, True, {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeRawReq(1)


def test_cancelRawReq_no_ethForCall(auto, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 0
    tx = auto.r.cancelRawReq(id, auto.FR_BOB)

    # Should've changed
    reqs = [NULL_REQ, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert auto.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]

    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelRawReq_with_ethForCall(auto, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 1

    tx = auto.r.cancelRawReq(id, auto.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, NULL_REQ, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert auto.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0



def test_cancelRawReq_payAUTO(auto, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 2

    tx = auto.r.cancelRawReq(id, auto.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, NULL_REQ, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert auto.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelRawReq_pay_AUTO_with_ethForCall(auto, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 3

    tx = auto.r.cancelRawReq(id, auto.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, reqPayAUTO, NULL_REQ, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert auto.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelRawReq_pay_AUTO_with_ethForCall_and_verifySender(auto, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 4

    tx = auto.r.cancelRawReq(id, auto.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, NULL_REQ]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert auto.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelRawReq_rev_not_requester(auto, stakedMin, reqsRaw):
    with reverts(REV_MSG_NOT_REQUESTER):
        auto.r.cancelRawReq(2, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})


# If it's already been executed, then Request.requester will be ETH_ADDR
def test_cancelRawReq_rev_already_executed(auto, stakedMin, reqsRaw):
    auto.r.cancelRawReq(2, {'from': auto.BOB, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_REQUESTER):
        auto.r.cancelRawReq(2, {'from': auto.BOB, 'gasPrice': INIT_GAS_PRICE_FAST})