from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_executeHashReqEth_no_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall) + msgValue - ethForExec
    assert asc.r.balance() == msgValue + ethForCall
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    assert asc.r.getHashedIpfsReqEth(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeHashReqEth_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall) + msgValue - ethForCall - ethForExec
    assert asc.r.balance() == msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    reqHashes[id] = NULL_HASH
    print(reqHashes)
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    assert asc.r.getHashedIpfsReqEth(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeHashReqEth_pay_ASC(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall)
    assert asc.r.balance() == (2 * msgValue) + ethForCall
    assert mockTarget.balance() == 0
    # ASC bals
    # Need to account for differences in division between Python and Solidity
    ASCForExecNotScaled = ((tx.return_value * tx.gas_price) + INIT_BASE_BOUNTY) * INIT_ETH_TO_ASCOIN_RATE
    ASCForExec = asc.r.divAOverB(ASCForExecNotScaled, E_18)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    reqHashes[id] = NULL_HASH
    print(reqHashes)
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    assert asc.r.getHashedIpfsReqEth(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeHashReqEth_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashReqEth(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall)
    assert asc.r.balance() == 2 * msgValue
    assert mockTarget.balance() == ethForCall
    # ASC bals
    # Need to account for differences in division between Python and Solidity
    ASCForExecNotScaled = ((tx.return_value * tx.gas_price) + INIT_BASE_BOUNTY) * INIT_ETH_TO_ASCOIN_RATE
    ASCForExec = asc.r.divAOverB(ASCForExecNotScaled, E_18)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    reqHashes[id] = NULL_HASH
    print(reqHashes)
    assert asc.r.getHashedIpfsReqsEth() == reqHashes
    assert asc.r.getHashedIpfsReqsEthLen() == 4
    assert asc.r.getHashedIpfsReqEth(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeHashReqEth_rev_already_executeHashReqEthd(asc, stakedMin, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth

    asc.r.executeHashReqEth(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashReqEth(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqEth_rev_not_executor(asc, stakedMin, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashReqEth(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})