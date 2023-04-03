from consts import *
from utils import *
from brownie import chain, reverts, web3


# Should execute with the default at the time newReq was created
def test_newReq_setDefaultPayIsAUTO_executeHashedReq(auto, mockTarget, evmMaths):
    ethForCall = E_18
    msgValue = ethForCall*2
    callData = mockTarget.setXPayFeeVerified.encode_input(3)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, True, False, False, False, "")
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, True, False, False, False, "", {'from': auto.BOB, 'value': msgValue})

    assert tx.events["HashedReqAdded"][0].values() == [0, *req]
    assert auto.r.getHashedReq(0) == keccakReq(auto, req)
    assert mockTarget.x() == 0

    callData = auto.o.setDefaultPayIsAUTO.encode_input(True)
    delay = 2*DAY
    args = (auto.o, 0, "", callData, chain.time() + delay + 60)
    auto.tl.queueTransaction(*args)
    chain.sleep(delay + 120)
    auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
    assert auto.o.defaultPayIsAUTO() == True

    expectedGas = auto.r.executeHashedReq.call(0, req, MIN_GAS, NULL_BYTES, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(0, req, expectedGas, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

    ethUsed = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
    assert auto.r.getHashedReq(0) == NULL_HASH
    assert mockTarget.x() == ethUsed