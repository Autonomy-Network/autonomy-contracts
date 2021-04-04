from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_cancelHashReqNoEth_no_ethForCall(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    id = 0
    tx = asc.r.cancelHashReqNoEth(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)

    # Should've changed
    assert asc.r.getHashedIpfsReqsNoEth() == [NULL_HASH]
    assert asc.r.getHashedIpfsReqsNoEthLen() == 1
    assert asc.r.getHashedIpfsReqNoEth(0) == NULL_HASH
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, False]

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
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASC.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE

    assert asc.r.getCumulRewardsOf(asc.ALICE) == 0
    assert asc.r.getCumulRewardsOf(asc.BOB) == 0
    assert asc.r.getCumulRewardsOf(asc.DENICE) == 0


def test_cancelHashReqNoEth_rev_req_not_the_same(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    # Alter the request
    invalidReq = list(req)
    invalidReq[6] = 1
    id = 0

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashReqNoEth(id, invalidReq, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashReqNoEth_rev_already_executed(asc, stakedMin, mockTarget, reqHashNoEth):
    _, staker, __ = stakedMin
    req, reqHashBytes = reqHashNoEth
    id = 0
    asc.r.executeHashReqNoEth(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashReqNoEth(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashReqNoEth_rev_not_the_requester(asc, stakedMin, mockTarget, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    id = 0

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashReqNoEth(id, req, *getIpfsMetaData(asc, req), asc.FR_ALICE)