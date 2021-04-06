from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def test_cancelRawReq_no_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 0
    tx = asc.r.cancelRawReq(id, asc.FR_BOB)

    # Should've changed
    reqs = [NULL_REQ, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    assert asc.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert asc.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]

    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY


def test_cancelRawReq_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 1

    tx = asc.r.cancelRawReq(id, asc.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, NULL_REQ, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    assert asc.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert asc.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY



def test_cancelRawReq_payASC(asc, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 2

    tx = asc.r.cancelRawReq(id, asc.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, NULL_REQ, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    assert asc.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert asc.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY


def test_cancelRawReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 3

    tx = asc.r.cancelRawReq(id, asc.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, reqPayASC, NULL_REQ, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    assert asc.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert asc.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY


def test_cancelRawReq_pay_ASC_with_ethForCall_and_verifySender(asc, stakedMin, mockTarget, reqsRaw):
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 4

    tx = asc.r.cancelRawReq(id, asc.FR_BOB)

    # Should've changed
    reqs = [reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, NULL_REQ]
    assert asc.r.getRawReqs() == reqs
    assert asc.r.getRawReqLen() == 5
    for i, req in enumerate(reqs):
        assert asc.r.getRawReq(i) == req
    assert tx.events["RawReqRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY


def test_cancelRawReq_rev_not_requester(asc, stakedMin, reqsRaw):
    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelRawReq(2, {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})


# If it's already been executed, then Request.requester will be ETH_ADDR
def test_cancelRawReq_rev_already_executed(asc, stakedMin, reqsRaw):
    asc.r.cancelRawReq(2, {'from': asc.BOB, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelRawReq(2, {'from': asc.BOB, 'gasPrice': TEST_GAS_PRICE})