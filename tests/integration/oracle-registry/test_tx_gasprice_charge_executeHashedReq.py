from consts import *
from utils import *
from brownie import chain, reverts, web3


def test_tx_gasprice_charge_executeHashedReq(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    callData = mockTarget.setX.encode_input(5)
    ethForCall = E_18
    msgValue = int(1.5 * ethForCall)
    initialBalance = auto.BOB.balance()
    request = [auto.BOB.address, mockTarget, auto.DENICE, callData, msgValue, 0, False, False, False, False]
    req = auto.r.newReq(mockTarget, auto.DENICE, callData, 0, False, False, False, {'from': auto.BOB, 'value': msgValue, 'gas_price': INIT_GAS_PRICE_FAST})
    req_gas_used = req.gas_used
    print(f'req_gas_used: {req_gas_used}')
    req_gas_price = req.gas_price
    print(f'req_gas_price: {req_gas_price}')
    balanceAfterCreate = auto.BOB.balance()

    print(f'initialBalance: {initialBalance}')
    print(f'balanceAfterCreate: {balanceAfterCreate}')

    request_id = req.events['HashedReqAdded']['id']
    print(f'request_id: {request_id}')

    exec = auto.r.executeHashedReq(request_id, request, MIN_GAS, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})
    gas_used = exec.gas_used
    print(f'gas_used: {gas_used}')
    gas_price = exec.gas_price
    print(f'gas_price: {gas_price}')

    newBalance = auto.BOB.balance()
    print(f'newBalance: {newBalance}')
    assert newBalance == initialBalance - (gas_used * gas_price) - (req_gas_used * req_gas_price)


# def test_updateGasPriceFast_lower_executeHashedReq_with_ethForCall(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
#     _, staker, __ = stakedMin
#     reqs, reqHashes, msgValue, ethForCall = hashedReqs
#     # reqHashes will modify the original even after this test has finished otherwise since it's a reference
#     reqHashes = reqHashes[:]
#     id = 1
#     assert mockTarget.x() == 0
#     assert auto.ALICE.balance() == INIT_ETH_BAL
#     assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (4 * ethForCall)
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0

#     assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST

#     newGasPriceFast = int(INIT_GAS_PRICE_FAST / 3)
#     callData = auto.po.updateGasPriceFast.encode_input(newGasPriceFast)
#     delay = 2*DAY
#     args = (auto.po, 0, "", callData, chain.time() + delay + 60)
#     auto.tl.queueTransaction(*args)
#     chain.sleep(delay + 120)
#     auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
#     assert auto.po.getGasPriceFast() == newGasPriceFast

#     expectedGas = auto.r.executeHashedReq.call(id, reqs[id], MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
#     tx = auto.r.executeHashedReq(id, reqs[id], expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
#     # Should've changed
#     # Eth bals
#     ethForExec = getEthForExec(evmMaths, tx, newGasPriceFast)
#     assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
#     assert auto.BOB.balance() == int(INIT_ETH_BAL - ((2 * msgValue) + (4 * ethForCall)) + msgValue - ethForCall - ethForExec)
#     assert auto.r.balance() == msgValue + (4 * ethForCall)
#     assert mockTarget.balance() == ethForCall
#     # AUTO bals
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0
#     # Target state
#     assert mockTarget.x() == 5
#     assert mockTarget.msgSender() == auto.r
#     # Registry state
#     reqHashes[id] = NULL_HASH
#     # Should revert when using indexes above the length
#     with reverts():
#         auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
#     assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
#     assert auto.r.getHashedReqs() == reqHashes
#     # Should revert when using indexes above the length
#     with reverts():
#         auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
#     assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
#     assert auto.r.getHashedReqsLen() == 9
#     assert auto.r.getHashedReq(id) == NULL_HASH
#     assert tx.events["HashedReqExecuted"][0].values() == [id, True]
#     # assert auto.r.getReqCountOf(auto.BOB) == 1
#     # assert auto.r.getExecCountOf(auto.ALICE) == 1
#     # assert auto.r.getReferalCountOf(auto.DENICE) == 1

#     # Shouldn't've changed
#     assert expectedGas == tx.return_value
#     assert mockTarget.userAddr() == ADDR_0


# def test_updateGasPriceFast_higher_executeHashedReq_payAUTO(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
#     _, staker, __ = stakedMin
#     reqs, reqHashes, msgValue, ethForCall = hashedReqs
#     # reqHashes will modify the original even after this test has finished otherwise since it's a reference
#     reqHashes = reqHashes[:]
#     id = 3
#     assert mockTarget.x() == 0
#     assert auto.ALICE.balance() == INIT_ETH_BAL
#     assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (4 * ethForCall)
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0

#     assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST

#     newGasPriceFast = int(INIT_GAS_PRICE_FAST * 1.3)
#     callData = auto.po.updateGasPriceFast.encode_input(newGasPriceFast)
#     delay = 2*DAY
#     args = (auto.po, 0, "", callData, chain.time() + delay + 60)
#     auto.tl.queueTransaction(*args)
#     chain.sleep(delay + 120)
#     auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
#     assert auto.po.getGasPriceFast() == newGasPriceFast

#     expectedGas = auto.r.executeHashedReq.call(id, reqs[id], MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
#     tx = auto.r.executeHashedReq(id, reqs[id], expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
#     # Should've changed
#     # Eth bals
#     assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
#     assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (4 * ethForCall))
#     assert auto.r.balance() == (2 * msgValue) + (3 * ethForCall)
#     assert mockTarget.balance() == ethForCall
#     # AUTO bals
#     AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, newGasPriceFast)
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0
#     # Target state
#     assert mockTarget.x() == 5
#     assert mockTarget.msgSender() == auto.r
#     # Registry state
#     reqHashes[id] = NULL_HASH
#     assert auto.r.getHashedReqs() == reqHashes
#     # Should revert when using indexes above the length
#     with reverts():
#         auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
#     assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
#     assert auto.r.getHashedReqsLen() == 9
#     assert auto.r.getHashedReq(id) == NULL_HASH
#     assert tx.events["HashedReqExecuted"][0].values() == [id, True]
#     # assert auto.r.getReqCountOf(auto.BOB) == 1
#     # assert auto.r.getExecCountOf(auto.ALICE) == 1
#     # assert auto.r.getReferalCountOf(auto.DENICE) == 1

#     # Shouldn't've changed
#     assert expectedGas == tx.return_value
#     assert mockTarget.userAddr() == ADDR_0


# def test_updateAUTOPerETH_higher_executeHashedReq_payAUTO(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
#     _, staker, __ = stakedMin
#     reqs, reqHashes, msgValue, ethForCall = hashedReqs
#     # reqHashes will modify the original even after this test has finished otherwise since it's a reference
#     reqHashes = reqHashes[:]
#     id = 3
#     assert mockTarget.x() == 0
#     assert auto.ALICE.balance() == INIT_ETH_BAL
#     assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (4 * ethForCall)
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0

#     assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI

#     newAUTOPerETH = int(INIT_AUTO_PER_ETH_WEI * 1.3)
#     callData = auto.po.updateAUTOPerETH.encode_input(newAUTOPerETH)
#     delay = 2*DAY
#     args = (auto.po, 0, "", callData, chain.time() + delay + 60)
#     auto.tl.queueTransaction(*args)
#     chain.sleep(delay + 120)
#     auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
#     assert auto.po.getAUTOPerETH() == newAUTOPerETH

#     expectedGas = auto.r.executeHashedReq.call(id, reqs[id], MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
#     tx = auto.r.executeHashedReq(id, reqs[id], expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
#     # Should've changed
#     # Eth bals
#     assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
#     assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (4 * ethForCall))
#     assert auto.r.balance() == (2 * msgValue) + (3 * ethForCall)
#     assert mockTarget.balance() == ethForCall
#     # AUTO bals
#     AUTOForExec = getAUTOForExec(evmMaths, tx, newAUTOPerETH, INIT_GAS_PRICE_FAST)
#     assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
#     assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
#     assert auto.AUTO.balanceOf(auto.DENICE) == 0
#     assert auto.AUTO.balanceOf(auto.r) == 0
#     # Target state
#     assert mockTarget.x() == 5
#     assert mockTarget.msgSender() == auto.r
#     # Registry state
#     reqHashes[id] = NULL_HASH
#     assert auto.r.getHashedReqs() == reqHashes
#     # Should revert when using indexes above the length
#     with reverts():
#         auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
#     assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
#     assert auto.r.getHashedReqsLen() == 9
#     assert auto.r.getHashedReq(id) == NULL_HASH
#     assert tx.events["HashedReqExecuted"][0].values() == [id, True]
#     # assert auto.r.getReqCountOf(auto.BOB) == 1
#     # assert auto.r.getExecCountOf(auto.ALICE) == 1
#     # assert auto.r.getReferalCountOf(auto.DENICE) == 1

#     # Shouldn't've changed
#     assert expectedGas == tx.return_value
#     assert mockTarget.userAddr() == ADDR_0