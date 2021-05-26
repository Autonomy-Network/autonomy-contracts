from consts import *
from utils import *
from brownie import chain, reverts, web3


def test_updateGasPriceFast_lower_executeRawReq_with_ethForCall(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
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

    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST

    newGasPriceFast = int(INIT_GAS_PRICE_FAST * 1.3)
    auto.po.updateGasPriceFast(newGasPriceFast)
    
    assert auto.po.getGasPriceFast() == newGasPriceFast

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(evmMaths, tx, newGasPriceFast)
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


def test_updateGasPriceFast_higher_executeRawReq_payAUTO(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
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

    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST

    newGasPriceFast = int(INIT_GAS_PRICE_FAST * 1.3)
    auto.po.updateGasPriceFast(newGasPriceFast)
    
    assert auto.po.getGasPriceFast() == newGasPriceFast

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, newGasPriceFast)
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


def test_updateAUTOPerETH_higher_executeRawReq_payAUTO(auto, evmMaths, stakedMin, mockTarget, reqsRaw):
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

    assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH

    newAUTOPerETH = int(INIT_AUTO_PER_ETH * 1.3)
    auto.po.updateAUTOPerETH(newAUTOPerETH)
    
    assert auto.po.getAUTOPerETH() == newAUTOPerETH

    tx = auto.r.executeRawReq(id, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, newAUTOPerETH, INIT_GAS_PRICE_FAST)
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