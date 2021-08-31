from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_recurring_payment_pay_ETH(auto, mockTarget, evmMaths):
    callData = mockTarget.useGasWithArray.encode_input(2)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, True)
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, True, True, {'from': auto.BOB, 'value': 0})

    id = 0
    assert tx.return_value == id
    assert tx.events["HashedReqAdded"][0].values() == [0, *req]
    hashes = [keccakReq(auto, req)]
    assert auto.r.getHashedReqs() == hashes
    assert auto.r.getHashedReqsSlice(0, len(hashes)) == hashes
    assert auto.r.getHashedReqsLen() == 1
    assert auto.r.getHashedReq(0) == hashes[0]

    cumulFee = 0

    for i in range(1, 6):
        expectedGas = auto.r.executeHashedReq.call(id, req, MIN_GAS, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})
        tx = auto.r.executeHashedReq(id, req, expectedGas, {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

        assert mockTarget.getGasWaster() == [0, 1]*i
        assert tx.events["HashedReqExecuted"][0].values() == [id, False]
        assert auto.r.getHashedReqs() == hashes
        assert auto.r.getHashedReqsSlice(0, len(hashes)) == hashes
        assert auto.r.getHashedReqsLen() == 1
        assert auto.r.getHashedReq(0) == hashes[0]

        AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
        print(AUTOForExec)
        cumulFee += AUTOForExec
        assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE + cumulFee
        assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - cumulFee