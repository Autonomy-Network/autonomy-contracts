from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_cancelHashedReqUnveri_no_ethForCall(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0
    tx = asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)

    # Should've changed
    reqHashesUnveri = [NULL_HASH]
    assert asc.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert asc.r.getHashedReqsUnveriLen() == 1
    assert asc.r.getHashedReqUnveri(0) == NULL_HASH
    assert tx.events["HashedReqUnveriRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReqUnveri_rev_req_not_the_same(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    # Alter the request
    invalidReq = list(req)
    invalidReq[6] = 1
    id = 0

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, invalidReq, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_already_executed(asc, stakedMin, mockTarget, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    id = 0
    asc.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_not_the_requester(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_ALICE)