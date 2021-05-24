from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Gotta put these these tests above test_executeHashedReqUnveri_pay_ASC since they don't
# need to use hashedReqUnveri first before running, and having tests that run any fixture
# before one that doesn't run it in the same file causes it to retain state from the
# fixture that it shouldn't


# Making a request that calls executeHashedReqUnveri should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of ASC should
# just make a new request for recursive ASCs, I see no reason to need to call executeHashedReqUnveri
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeHashedReqUnveri_rev_nonReentrant(asc, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes1 = addReqGetHashBytes(asc, req1)

    asc.r.newHashedReqUnveri(reqHashBytes1, {'from': asc.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteHashedReqUnveri.encode_input(0, req1, *getIpfsMetaData(asc, req1))
    req2 = (asc.BOB.address, mockReentrancyAttack.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes2 = addReqGetHashBytes(asc, req2)

    asc.r.newHashedReqUnveri(reqHashBytes2, {'from': asc.BOB})

    print(asc.sm.getExecutor())
    print(asc.sm.getStakes())
    print(asc.sm.getUpdatedExecRes())

    with reverts(REV_MSG_REENTRANCY):
        asc.r.executeHashedReqUnveri(1, req2, *getIpfsMetaData(asc, req2))


def test_executeHashedReqUnveri_returns_revert_message(asc, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
    callData = mockTarget.revertWithMessage.encode_input()
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)

    tx = asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_GOOFED):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_returns_no_revert_message(asc, stakedMin, mockTarget):
    _, staker, __ = stakedMin

    asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
    callData = mockTarget.revertWithoutMessage.encode_input()
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)

    tx = asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(''):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_initEthSent(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 1, 0, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_ethForCall(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 1, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_payWithASC(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, False)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_verifySender(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, True, True)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_pay_ASC(asc, stakedMin, mockTarget, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.r.balance() == 0
    assert mockTarget.balance() == 0
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD, INIT_GAS_PRICE_FAST)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqHashesUnveri = [NULL_HASH]
    assert asc.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert asc.r.getHashedReqsUnveriLen() == 1
    assert asc.r.getHashedReqUnveri(id) == NULL_HASH
    assert tx.events["HashedReqUnveriRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReqUnveri_rev_target_is_registry(asc, mockTarget, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, asc.r.address, asc.DENICE, callData, 0, 0, False, True)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_target_is_ASCoin(asc, mockTarget, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, asc.ASC.address, asc.DENICE, callData, 0, 0, False, True)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_not_executor(asc, stakedMin, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.DENICE, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_req_not_the_same(asc, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    invalidReq = list(req)
    invalidReq[6] = 1
    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReqUnveri(0, invalidReq, *getIpfsMetaData(asc, invalidReq), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_already_executed(asc, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri

    asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReqUnveri_rev_noFish(asc, vulnerableRegistry, vulnerableHashedReqUnveri, stakedMin):
    _, staker, __ = stakedMin
    req, reqHashBytes = vulnerableHashedReqUnveri
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
