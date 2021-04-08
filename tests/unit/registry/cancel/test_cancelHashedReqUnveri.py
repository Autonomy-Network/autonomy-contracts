from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_cancelHashedReqUnveri_no_ethForCall(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    id = 0
    tx = asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)

    # Should've changed
    assert asc.r.getHashedReqsUnveri() == [NULL_HASH]
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

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY


def test_cancelHashedReqUnveri_rev_req_not_the_same(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    # Alter the request
    invalidReq = list(req)
    invalidReq[6] = 1
    id = 0

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, invalidReq, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_already_executed(asc, stakedMin, mockTarget, reqHashNoEth):
    _, staker, __ = stakedMin
    req, reqHashBytes = reqHashNoEth
    id = 0
    asc.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_not_the_requester(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    id = 0

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_ALICE)