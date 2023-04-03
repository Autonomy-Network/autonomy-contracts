from consts import *
from utils import *
from brownie import chain, reverts, web3


def test_executeHashedReq_wait_executeHashedReq(a, auto, evmMaths, stakedMultiSmall, hashedReqs):
    nums, stakers, startStakes, _ = stakedMultiSmall
    reqs, reqHashes, msgValue, ethForCall = hashedReqs

    # Go to the start of an epoch so the executor doesn't change midway and obsolete this test
    chain.mine(BLOCKS_IN_EPOCH - (bn() % BLOCKS_IN_EPOCH) - 1)
    
    newExec = getExecutor(evmMaths, bn() + 1, startStakes, None)[0]
    id = 0
    # Make sure execution reverts whenever called by everyone except the actual executor
    for addr in a:
        if addr != newExec:
            with reverts(REV_MSG_NOT_EXEC):
                auto.r.executeHashedReq(id, reqs[id], "", MIN_GAS, {'from': addr, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Execution should succeed with the actual executor
    auto.r.executeHashedReq(id, reqs[id], "", MIN_GAS, {'from': newExec, 'gasPrice': INIT_GAS_PRICE_FAST})

    chain.mine(BLOCKS_IN_EPOCH - (bn() % BLOCKS_IN_EPOCH) - 1)

    newExec = getExecutor(evmMaths, bn() + 1, startStakes, newExec)[0]
    id = 1
    # Make sure execution reverts whenever called by everyone except the actual executor
    for addr in a:
        if addr != newExec:
            with reverts(REV_MSG_NOT_EXEC):
                auto.r.executeHashedReq(id, reqs[id], "", MIN_GAS, {'from': addr, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Execution should succeed with the actual executor
    auto.r.executeHashedReq(id, reqs[id], "", MIN_GAS, {'from': newExec, 'gasPrice': INIT_GAS_PRICE_FAST})