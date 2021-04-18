from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeRawReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of ASC should
# just make a new request for recursive ASCs, I see no reason to need to call executeRawReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeRawReq_rev_nonReentrant(asc, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB})
    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteRawReq.encode_input(0)
    asc.r.newRawReq(mockReentrancyAttack, callData, False, True, 0, asc.DENICE, {'from': asc.BOB})

    with reverts(REV_MSG_REENTRANCY):
        asc.r.executeRawReq(1)


def test_executeRawReq_no_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_ETH_PER_USD)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqs = [NULL_REQ, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 5
    assert asc.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeRawReq_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 1
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_ETH_PER_USD)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForCall - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqs = [reqNoEthForCall, NULL_REQ, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 5
    assert asc.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeRawReq_pay_ASC(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 2
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, NULL_REQ, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 5
    assert asc.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeRawReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 3
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, reqPayASC, NULL_REQ, reqPayASCEthForCallVerifySender]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 5
    assert asc.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeRawReq_pay_ASC_with_ethForCall_and_verifySender(asc, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 4
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.userAddr() == asc.BOB.address
    assert mockTarget.msgSender() == asc.vf.address
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, reqPayASC, reqPayASCEthForCall, NULL_REQ]
    assert asc.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, len(reqs) + 1)
    assert asc.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert asc.r.getRawReqLen() == 5
    assert asc.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.x() == 0



def test_executeRawReq_rev_already_executed(asc, stakedMin, reqsRaw):
    _, staker, __ = stakedMin
    asc.r.executeRawReq(2, {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_ALREADY_EXECUTED):
        asc.r.executeRawReq(2, {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeRawReq_rev_not_executor(asc, stakedMin, reqsRaw):
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeRawReq(2, {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


def test_executeRawReq_rev_noFish_pay_eth(asc, vulnerableRegistry, vulnerableReqsRaw, stakedMin):
    _, staker, __ = stakedMin
    reqEthForCall, reqPayASCEthForCall, msgValue, ethForCall = vulnerableReqsRaw
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeRawReq_rev_noFish_payWithASC(asc, vulnerableRegistry, vulnerableReqsRaw, stakedMin):
    _, staker, __ = stakedMin
    reqEthForCall, reqPayASCEthForCall, msgValue, ethForCall = vulnerableReqsRaw
    id = 1

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeRawReq(id, {'from': staker, 'gasPrice': TEST_GAS_PRICE})