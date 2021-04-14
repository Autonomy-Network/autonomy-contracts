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
    asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB})
    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecute.encode_input(0)
    req = (asc.BOB.address, mockReentrancyAttack.address, callData, False, True, 0, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)

    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB})

    with reverts(REV_MSG_REENTRANCY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req))


def test_executeHashedReqUnveri_rev_initEthSent(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, False, True, 1, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_ethForCall(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 1, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_payWithASC(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, False, False, 0, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_verifySender(asc, mockTarget, stakedMin):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, callData, True, True, 0, 0, asc.DENICE.address)
    reqHashBytes = addReqGetHashBytes(asc, req)
    asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    with reverts(REV_MSG_CANNOT_VERIFY):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


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

    tx = asc.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.r.balance() == 0
    assert mockTarget.balance() == 0
    # ASC bals
    # Need to account for differences in division between Python and Solidity
    ASCForExecNotScaled = ((tx.return_value * tx.gas_price) + INIT_BASE_BOUNTY) * INIT_ETH_TO_ASCOIN_RATE
    ASCForExec = asc.r.divAOverB(ASCForExecNotScaled, E_18)
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
    req = (asc.BOB.address, asc.r.address, callData, False, True, 0, 0, asc.DENICE.address)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_target_is_ASCoin(asc, mockTarget, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, asc.ASC.address, callData, False, True, 0, 0, asc.DENICE.address)

    with reverts(REV_MSG_TARGET):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_not_executor(asc, stakedMin, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_req_not_the_same(asc, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    invalidReq = list(req)
    invalidReq[6] = 1
    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReqUnveri(0, invalidReq, *getIpfsMetaData(asc, invalidReq), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_already_executed(asc, stakedMin, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri

    asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReqUnveri_rev_noFish(asc, vulnerableRegistry, vulnerableHashedReqUnveri, stakedMin):
    _, staker, __ = stakedMin
    req, reqHashBytes = vulnerableHashedReqUnveri
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
