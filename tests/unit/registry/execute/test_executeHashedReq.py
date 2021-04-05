from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Randomly generate addresses for the sender and calldata input independently
# to test validCalldata upon calling executeHashedReq
@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_executeHashedReq_validCalldata(asc, stakedMin, mockTarget, ethForCall, payWithASC, userAddr, sender):
    # It's gonna be a pain in the ass to do the accounting if they're equal
    if sender != asc.ALICE and sender != asc.DENICE:
        _, staker, __ = stakedMin

        msgValue = ethForCall + E_18
        if payWithASC:
            msgValue = ethForCall

        id = 0
        callData = mockTarget.setAddrPayVerified.encode_input(userAddr)
        req = (sender.address, mockTarget.address, callData, True, payWithASC, msgValue, ethForCall, asc.DENICE.address)
        addToIpfs(asc, req)

        asc.ASC.approve(asc.r, MAX_TEST_STAKE, {'from': sender})
        asc.ASC.transfer(sender, MAX_TEST_STAKE, asc.FR_DEPLOYER)
        senderASCStartBal = asc.ASC.balanceOf(sender)
        asc.r.newHashedReq(mockTarget, callData, True, payWithASC, ethForCall, asc.DENICE, *getIpfsMetaData(asc, req), {'from': sender, 'value': msgValue})

        if userAddr != sender:
            with reverts(REV_MSG_CALLDATA_NOT_VER):
                asc.r.executeHashedReq(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
        else:
            tx = asc.r.executeHashedReq(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

            ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
            assert mockTarget.balance() == ethForCall
            if payWithASC:
                # Eth bals
                assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall
                # ASC bals
                ASCForExecNotScaled = ((tx.return_value * tx.gas_price) + INIT_BASE_BOUNTY) * INIT_ETH_TO_ASCOIN_RATE
                ASCForExec = asc.r.divAOverB(ASCForExecNotScaled, E_18)
                assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
                assert asc.ASC.balanceOf(sender) - senderASCStartBal == -ASCForExec
                assert asc.ASC.balanceOf(asc.DENICE) == 0
                assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
            else:
                # Eth bals
                assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall - ethForExec
                # ASC bals
                assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
                assert asc.ASC.balanceOf(sender) - senderASCStartBal == 0
                assert asc.ASC.balanceOf(asc.DENICE) == 0
                assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

            # Target state
            assert mockTarget.userAddr() == sender.address
            assert mockTarget.msgSender() == asc.vf.address
            # Registry state
            assert asc.r.getHashedReqs() == [NULL_HASH]
            assert asc.r.getHashedReqsLen() == 1
            assert asc.r.getHashedReq(id) == NULL_HASH
            assert asc.r.getCumulRewardsOf(sender) == INIT_REQUESTER_REWARD
            assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
            assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
            assert tx.events["HashedReqRemoved"][0].values() == [id, True]

            # Shouldn't've changed
            assert mockTarget.x() == 0
            assert asc.r.balance() == 0
            assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
            assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
            assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_no_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.uvf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = (tx.return_value * tx.gas_price) + (INIT_BASE_BOUNTY * 2)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForCall - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.uvf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_pay_ASC(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == (2 * msgValue) + (2 * ethForCall)
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
    assert mockTarget.msgSender() == asc.uvf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
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
    assert mockTarget.msgSender() == asc.uvf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_pay_ASC_with_ethForCall_and_verifySender(asc, stakedMin, mockTarget, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 4
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == INIT_ASC_REW_POOL

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
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
    assert mockTarget.userAddr() == asc.BOB.address
    assert mockTarget.msgSender() == asc.vf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert asc.r.getCumulRewardsOf(asc.BOB) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.DENICE) == INIT_REQUESTER_REWARD
    assert asc.r.getCumulRewardsOf(asc.ALICE) == INIT_EXECUTOR_REWARD
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD


def test_executeHashedReq_rev_not_executor(asc, stakedMin, reqsHashEth):
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_req_not_the_same(asc, stakedMin, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth
    invalidReq = list(reqs[0])
    invalidReq[6] = 1
    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReq(0, invalidReq, *getIpfsMetaData(asc, invalidReq), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_already_executeHashedReqd(asc, stakedMin, reqsHashEth):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = reqsHashEth

    asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})