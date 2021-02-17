from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def test_execute_no_ethForCall(asc, stakedMin, mockTarget, requestsEth):
    _, staker, __ = stakedMin
    requestNoEthForCall, requestEthForCall, requestPayASC, valueSent, ethForCall = requestsEth
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    gasPrice = 10**9

    tx = asc.r.execute(0, {'from': staker, 'gasPrice': gasPrice})

    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) + valueSent - ethForExec
    assert asc.r.balance() == valueSent
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target storage
    assert mockTarget.x() == 5
    # Registry storage
    assert asc.r.getRequests() == [NULL_REQ, requestEthForCall, requestPayASC]
    assert asc.r.getRequestsLength() == 3
    assert asc.r.getRequest(0) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RequestRemoved"][0].values() == [0, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_execute_with_ethForCall(asc, stakedMin, mockTarget, requestsEth):
    _, staker, __ = stakedMin
    requestNoEthForCall, requestEthForCall, requestPayASC, valueSent, ethForCall = requestsEth
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    gasPrice = 10**9

    tx = asc.r.execute(1, {'from': staker, 'gasPrice': gasPrice})

    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) + valueSent - ethForCall - ethForExec
    assert asc.r.balance() == valueSent
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target storage
    assert mockTarget.x() == 5
    # Registry storage
    assert asc.r.getRequests() == [requestNoEthForCall, NULL_REQ, requestPayASC]
    assert asc.r.getRequestsLength() == 3
    assert asc.r.getRequest(1) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RequestRemoved"][0].values() == [1, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_execute_pay_ASC(asc, stakedMin, mockTarget, requestsEth):
    _, staker, __ = stakedMin
    requestNoEthForCall, requestEthForCall, requestPayASC, valueSent, _ = requestsEth
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    gasPrice = 10**9

    tx = asc.r.execute(2, {'from': staker, 'gasPrice': gasPrice})

    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent)
    assert asc.r.balance() == 2 * valueSent
    assert mockTarget.balance() == 0
    # ASC bals
    # Need to account for differences in division between Python and Solidity
    ASCForExecNotScaled = ((tx.return_value * tx.gas_price) + INIT_BASE_BOUNTY) * INIT_ETH_TO_ASCOIN_RATE
    ASCForExec = asc.r.divAOverB(ASCForExecNotScaled, E_18)
    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target storage
    assert mockTarget.x() == 5
    # Registry storage
    assert asc.r.getRequests() == [requestNoEthForCall, requestEthForCall, NULL_REQ]
    assert asc.r.getRequestsLength() == 3
    assert asc.r.getRequest(2) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RequestRemoved"][0].values() == [2, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE
