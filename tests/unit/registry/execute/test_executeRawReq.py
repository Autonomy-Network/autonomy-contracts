from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeRawReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call executeRawReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeRawReq_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, True, {'from': auto.BOB})
    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteRawReq.encode_input(0)
    auto.r.newRawReq(mockReentrancyAttack, auto.DENICE, callData, 0, False, True, {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeRawReq(1)


def test_executeRawReq_returns_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    callData = mockTarget.revertWithMessage.encode_input()
    auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, False, {'from': auto.BOB, 'value': E_18})

    with reverts(REV_MSG_GOOFED):
        auto.r.executeRawReq(0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeRawReq_returns_no_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    callData = mockTarget.revertWithMessage.encode_input()
    auto.r.newRawReq(mockTarget, auto.DENICE, callData, 0, False, False, {'from': auto.BOB, 'value': E_18})

    with reverts(''):
        auto.r.executeRawReq(0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeRawReq_no_ethForCall(auto, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 0
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
    assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForExec
    assert auto.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqs = [NULL_REQ, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    assert auto.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeRawReq_with_ethForCall(auto, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 1
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
    assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForCall - ethForExec
    assert auto.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqs = [reqNoEthForCall, NULL_REQ, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    assert auto.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeRawReq_pay_AUTO(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 2
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, NULL_REQ, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    assert auto.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeRawReq_pay_AUTO_with_ethForCall(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 3
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, reqPayAUTO, NULL_REQ, reqPayAUTOEthForCallVerifySender]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    assert auto.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeRawReq_pay_AUTO_with_ethForCall_and_verifySender(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
    _, staker, __ = stakedMin
    reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, reqPayAUTOEthForCallVerifySender, msgValue, ethForCall = reqsRaw
    id = 4
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.userAddr() == auto.BOB.address
    assert mockTarget.msgSender() == auto.vf.address
    # Registry state
    reqs = [reqNoEthForCall, reqEthForCall, reqPayAUTO, reqPayAUTOEthForCall, NULL_REQ]
    assert auto.r.getRawReqs() == reqs
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getRawReqsSlice(0, len(reqs) + 1)
    assert auto.r.getRawReqsSlice(0, len(reqs)) == reqs
    assert auto.r.getRawReqLen() == 5
    assert auto.r.getRawReq(id) == NULL_REQ
    assert tx.events["RawReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.x() == 0


def test_executeRawReq_rev_already_executed(auto, stakedMin, reqsRaw):
    _, staker, __ = stakedMin
    auto.r.executeRawReq(2, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_ALREADY_EXECUTED):
        auto.r.executeRawReq(2, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeRawReq_rev_not_executor(auto, stakedMin, reqsRaw):
    with reverts(REV_MSG_NOT_EXEC):
        auto.r.executeRawReq(2, {'from': auto.DENICE, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeRawReq_rev_noFish_pay_eth(auto, vulnerableRegistry, vulnerableReqsRaw, stakedMin):
    _, staker, __ = stakedMin
    reqEthForCall, reqPayAUTOEthForCall, msgValue, ethForCall = vulnerableReqsRaw
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeRawReq_rev_noFish_payWithAUTO(auto, vulnerableRegistry, vulnerableReqsRaw, stakedMin):
    _, staker, __ = stakedMin
    reqEthForCall, reqPayAUTOEthForCall, msgValue, ethForCall = vulnerableReqsRaw
    id = 1

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})