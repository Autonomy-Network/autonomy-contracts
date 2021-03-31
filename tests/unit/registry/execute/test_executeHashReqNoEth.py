from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Gotta put these reverts above test_executeHashReqNoEth_pay_ASC since they don't
# need to use reqHashNoEth first before running, and having tests that run any fixture
# before one that doesn't run it in the same file causes it to retain state from the
# fixture that it shouldn't

def test_executeHashReqNoEth_rev_initEthSent(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, True, 1, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashReqNoEth(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_NO_ETH):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_rev_ethForCall(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, True, 0, 1, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashReqNoEth(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_NO_ETH):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_rev_payWithASC(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, False, 0, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashReqNoEth(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_NO_ETH):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_pay_ASC(asc, stakedMin, mockTarget, reqHashNoEth):
    _, staker, __ = stakedMin
    req, reqHashBytes = reqHashNoEth
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashReqNoEth(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.r.balance() == 0
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
    assert asc.r.getHashedIpfsReqsNoEth() == [NULL_HASH]
    assert asc.r.getHashedIpfsReqsNoEthLen() == 1
    assert asc.r.getHashedIpfsReqNoEth(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqNoEthRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE


def test_executeHashReqNoEth_rev_target_is_registry(asc, mockTarget, stakedMin, reqHashNoEth):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, asc.r.address, callData, True, 0, 0, asc.DENICE.address)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_rev_target_is_ASCoin(asc, mockTarget, stakedMin, reqHashNoEth):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, asc.ASC.address, callData, True, 0, 0, asc.DENICE.address)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_rev_not_executor(asc, stakedMin, reqHashNoEth):
    req, reqHashBytes = reqHashNoEth
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashReqNoEth_rev_already_executed(asc, stakedMin, reqHashNoEth):
    _, staker, __ = stakedMin
    req, reqHashBytes = reqHashNoEth

    asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashReqNoEth(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})