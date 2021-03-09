from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def test_cancel_no_ethForCall(asc, stakedMin, mockTarget, requests):
    requestNoEthForCall, requestEthForCall, requestPayASC, requestPayASCEthForCall, valueSent, ethForCall = requests
    id = 0
    tx = asc.r.cancel(id, asc.FR_BOB)

    # Should've changed
    reqs = [NULL_REQ, requestEthForCall, requestPayASC, requestPayASCEthForCall]
    assert asc.r.getRawRequests() == reqs
    assert asc.r.getRawRequestsLen() == 4
    for i, req in enumerate(reqs):
        assert asc.r.getRawRequest(i) == req
    assert tx.events["RequestRemoved"][0].values() == [id, False]

    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) - ethForCall + valueSent

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASCoin.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE

    assert asc.r.getCumulRewardsOf(asc.ALICE) == 0
    assert asc.r.getCumulRewardsOf(asc.BOB) == 0
    assert asc.r.getCumulRewardsOf(asc.DENICE) == 0


def test_cancel_with_ethForCall(asc, stakedMin, mockTarget, requests):
    requestNoEthForCall, requestEthForCall, requestPayASC, requestPayASCEthForCall, valueSent, ethForCall = requests
    id = 1

    tx = asc.r.cancel(id, asc.FR_BOB)

    # Should've changed
    reqs = [requestNoEthForCall, NULL_REQ, requestPayASC, requestPayASCEthForCall]
    assert asc.r.getRawRequests() == reqs
    assert asc.r.getRawRequestsLen() == 4
    for i, req in enumerate(reqs):
        assert asc.r.getRawRequest(i) == req
    assert tx.events["RequestRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) - ethForCall + valueSent

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASCoin.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE

    assert asc.r.getCumulRewardsOf(asc.ALICE) == 0
    assert asc.r.getCumulRewardsOf(asc.BOB) == 0
    assert asc.r.getCumulRewardsOf(asc.DENICE) == 0



def test_cancel_payASC(asc, stakedMin, mockTarget, requests):
    requestNoEthForCall, requestEthForCall, requestPayASC, requestPayASCEthForCall, valueSent, ethForCall = requests
    id = 2

    tx = asc.r.cancel(id, asc.FR_BOB)

    # Should've changed
    reqs = [requestNoEthForCall, requestEthForCall, NULL_REQ, requestPayASCEthForCall]
    assert asc.r.getRawRequests() == reqs
    assert asc.r.getRawRequestsLen() == 4
    for i, req in enumerate(reqs):
        assert asc.r.getRawRequest(i) == req
    assert tx.events["RequestRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) - ethForCall
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASCoin.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE

    assert asc.r.getCumulRewardsOf(asc.ALICE) == 0
    assert asc.r.getCumulRewardsOf(asc.BOB) == 0
    assert asc.r.getCumulRewardsOf(asc.DENICE) == 0


def test_cancel_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, requests):
    requestNoEthForCall, requestEthForCall, requestPayASC, requestPayASCEthForCall, valueSent, ethForCall = requests
    id = 3

    tx = asc.r.cancel(id, asc.FR_BOB)

    # Should've changed
    reqs = [requestNoEthForCall, requestEthForCall, requestPayASC, NULL_REQ]
    assert asc.r.getRawRequests() == reqs
    assert asc.r.getRawRequestsLen() == 4
    for i, req in enumerate(reqs):
        assert asc.r.getRawRequest(i) == req
    assert tx.events["RequestRemoved"][0].values() == [id, False]
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * valueSent) - ethForCall + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASCoin.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL
    assert asc.ASCoin.balanceOf(mockTarget) == 0

    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE

    assert asc.r.getCumulRewardsOf(asc.ALICE) == 0
    assert asc.r.getCumulRewardsOf(asc.BOB) == 0
    assert asc.r.getCumulRewardsOf(asc.DENICE) == 0
