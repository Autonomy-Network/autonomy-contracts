from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Gotta put these these tests above test_executeHashedReqUnveri_pay_AUTO since they don't
# need to use hashedReqUnveri first before running, and having tests that run any fixture
# before one that doesn't run it in the same file causes it to retain state from the
# fixture that it shouldn't


# Making a request that calls executeHashedReqUnveri should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call executeHashedReqUnveri
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeHashedReqUnveri_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False)
    reqHashBytes1 = addReqGetHashBytes(auto, req1)

    auto.r.newHashedReqUnveri(reqHashBytes1, {'from': auto.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteHashedReqUnveri.encode_input(0, req1, *getIpfsMetaData(auto, req1), MIN_GAS)
    req2 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE, callData, 0, 0, False, False, True, False)
    reqHashBytes2 = addReqGetHashBytes(auto, req2)

    auto.r.newHashedReqUnveri(reqHashBytes2, {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeHashedReqUnveri(1, req2, *getIpfsMetaData(auto, req2), MIN_GAS)


def test_executeHashedReqUnveri_returns_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    callData = mockTarget.revertWithMessage.encode_input()
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False)
    reqHashBytes = addReqGetHashBytes(auto, req)

    tx = auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(REV_MSG_GOOFED):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_returns_no_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    callData = mockTarget.revertWithoutMessage.encode_input()
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False)
    reqHashBytes = addReqGetHashBytes(auto, req)

    tx = auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(''):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_initEthSent(auto, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 1, 0, False, False, True, False)
    reqHashBytes = addReqGetHashBytes(auto, req)
    auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_ethForCall(auto, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 1, False, False, True, False)
    reqHashBytes = addReqGetHashBytes(auto, req)
    auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_payWithAUTO(auto, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, False, False)
    reqHashBytes = addReqGetHashBytes(auto, req)
    auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_verifySender(auto, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, True, False, True, False)
    reqHashBytes = addReqGetHashBytes(auto, req)
    auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_pay_AUTO(auto, evmMaths, stakedMin, mockTarget, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    id = 0
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    expectedGas = auto.r.executeHashedReqUnveri.call(id, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    tx = auto.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.r.balance() == 0
    assert mockTarget.balance() == 0
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqHashesUnveri = [NULL_HASH]
    assert auto.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert auto.r.getHashedReqsUnveriLen() == 1
    assert auto.r.getHashedReqUnveri(id) == NULL_HASH
    assert tx.events["HashedReqUnveriExecuted"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReqUnveri_rev_target_is_registry(auto, mockTarget, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, auto.r.address, auto.DENICE, callData, 0, 0, False, False, True, False)

    with reverts(REV_MSG_TARGET):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_target_is_AUTO(auto, mockTarget, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, auto.AUTO.address, auto.DENICE, callData, 0, 0, False, False, True, False)

    with reverts(REV_MSG_TARGET):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_not_executor(auto, stakedMin, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    with reverts(REV_MSG_NOT_EXEC):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': auto.DENICE, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_req_not_the_same(auto, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    invalidReq = list(req)
    invalidReq[6] = 1
    with reverts(REV_MSG_NOT_SAME_IPFS):
        auto.r.executeHashedReqUnveri(0, invalidReq, *getIpfsMetaData(auto, invalidReq), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_already_executed(auto, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri

    auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME_IPFS):
        auto.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_hacked(auto, vulnerableRegistry, vulnerableHashedReqUnveri, stakedMin):
    _, staker, __ = stakedMin
    req, reqHashBytes = vulnerableHashedReqUnveri
    id = 0

    with reverts(REV_MSG_OVERFLOW):
        vulnerableRegistry.executeHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), MIN_GAS, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
