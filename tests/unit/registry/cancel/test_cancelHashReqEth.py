from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_cancelHashReqEth_no_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    tx = asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedIpfsReqEth(i) == reqHash
    assert tx.events["HashedReqEthRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
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


def test_cancelHashReqEth_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1

    tx = asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedIpfsReqEth(i) == reqHash
    assert tx.events["HashedReqEthRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
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



def test_cancelHashReqEth_payASC(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2

    tx = asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedIpfsReqEth(i) == reqHash
    assert tx.events["HashedReqEthRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
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


def test_cancelHashReqEth_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3

    tx = asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    for i, reqHash in enumerate(reqHashes):
        assert asc.r.getHashedIpfsReqEth(i) == reqHash
    assert tx.events["HashedReqEthRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
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


def test_cancelHashReqEth_rev_req_not_the_same(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    id = 1

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashReqEth(id, reqs[2], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)


def test_cancelHashReqEth_rev_already_executed(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    id = 1
    asc.r.executeHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_BOB)


def test_cancelHashReqEth_rev_not_the_requester(asc, stakedMin, mockTarget, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    id = 1

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), asc.FR_ALICE)