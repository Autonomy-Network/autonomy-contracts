from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_cancelHashedReq_no_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    tx = asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
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
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReq_with_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1

    tx = asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
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
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReq_payASC(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2

    tx = asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]

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
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3

    tx = asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
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
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReq_pay_ASC_with_ethForCall_and_verifySender(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 4

    tx = asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
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
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReq_rev_req_not_the_same(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReq(id, reqs[2], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)


def test_cancelHashedReq_rev_already_executed(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1
    asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)


def test_cancelHashedReq_rev_not_the_requester(asc, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_ALICE)