from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *
import eth_abi


def test_injecting_address_array(auto, stakedMin, mockTarget, evmMaths):
    _, staker, __ = stakedMin
    callData = mockTarget.setArrInjectedData.encode_input()
    mock_api_url = "pingme.com"
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, E_18, 0, False, False, False, False, True, mock_api_url)
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, False, False, True, mock_api_url, {'from': auto.BOB, 'value': E_18})


    id = 0
    assert tx.return_value == id
    assert tx.events["HashedReqAdded"][0].values() == [0, *req]
    hashes = [keccakReq(auto, req)]
    assert auto.r.getHashedReqs() == hashes
    assert auto.r.getHashedReqsSlice(0, len(hashes)) == hashes
    assert auto.r.getHashedReqsLen() == 1
    assert auto.r.getHashedReq(0) == hashes[0]
    print(mockTarget.getAddrArr())
    assert mockTarget.getAddrArr() == []

    arr = [auto.ALICE.address, auto.BOB.address, auto.CHARLIE.address]
    arr_encoded = mockTarget.dummyAddrArrInput.encode_input(arr)[10:]
    expectedGas = auto.r.executeHashedReq.call(id, req, arr_encoded, MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReq(id, req, arr_encoded, expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    assert mockTarget.getAddrArr() == arr
