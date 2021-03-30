from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def test_executeRawReq_no_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, msgValue, ethForCall = reqsRaw
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - ethForCall
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall) + msgValue - ethForExec
    assert asc.r.balance() == msgValue + ethForCall
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    assert asc.r.getRawRequests() == [NULL_REQ, reqEthForCall, reqPayASC, reqPayASCEthForCall]
    assert asc.r.getRawRequestsLen() == 4
    assert asc.r.getRawRequest(id) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RawReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeRawReq_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, msgValue, ethForCall = reqsRaw
    id = 1
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall) + msgValue - ethForCall - ethForExec
    assert asc.r.balance() == msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    assert asc.r.getRawRequests() == [reqNoEthForCall, NULL_REQ, reqPayASC, reqPayASCEthForCall]
    assert asc.r.getRawRequestsLen() == 4
    assert asc.r.getRawRequest(id) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RawReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeRawReq_pay_ASC(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, msgValue, ethForCall = reqsRaw
    id = 2
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

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
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    assert asc.r.getRawRequests() == [reqNoEthForCall, reqEthForCall, NULL_REQ, reqPayASCEthForCall]
    assert asc.r.getRawRequestsLen() == 4
    assert asc.r.getRawRequest(id) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RawReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeRawReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, msgValue, ethForCall = reqsRaw
    id = 3
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

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
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    # Registry state
    assert asc.r.getRawRequests() == [reqNoEthForCall, reqEthForCall, reqPayASC, NULL_REQ]
    assert asc.r.getRawRequestsLen() == 4
    assert asc.r.getRawRequest(id) == NULL_REQ
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["RawReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeRawReq_rev_already_executeRawReqd(asc, stakedMin, reqsRaw):
    _, staker, __ = stakedMin
    asc.r.executeRawReq(2, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_ALREADY_EXECUTED):
        asc.r.executeRawReq(2, {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeRawReq_rev_not_executor(asc, stakedMin, reqsRaw):
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeRawReq(2, {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


# For some reason this test produces an error in Brownie, presumed to be
# a bug in Brownie
# # Making a request that calls executeRawReq should be banned to reduce attack surface
# # and generally prevent unknown funny business. Any 'legitimate' use of ASC should
# # just make a new request for recursive ASCs, I see no reason to need to call executeRawReq
# # from a request etc. Can't make a call directly to the registry from the registry
# # because of `targetNotThis`, so need to call into it from a new contract
# def test_executeRawReq_rev_nonReentrant(asc, stakedMin, reqsRaw, mockReentrancyAttack):
#     _, staker, __ = stakedMin
#     callData = mockReentrancyAttack.callExecute.encode_input(2)
#     asc.r.newRawRequest(mockReentrancyAttack, callData, True, 0, asc.DENICE, {'from': asc.BOB})

#     with reverts(REV_MSG_NOT_EXEC):
#         asc.r.executeRawReq(4, {'from': staker, 'gasPrice': TEST_GAS_PRICE})
#     # reqPayASC = (asc.BOB.address, asc.r.address, callData, True, 0, 0, asc.DENICE.address)