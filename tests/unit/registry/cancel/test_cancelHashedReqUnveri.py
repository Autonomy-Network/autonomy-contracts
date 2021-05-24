from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeHashedReqUnveri should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of ASC should
# just make a new request for recursive ASCs, I see no reason to need to call executeHashedReqUnveri
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_cancelHashedReqUnveri_rev_nonReentrant(asc, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (asc.BOB.address, mockTarget.address, asc.DENICE.address, callData, False, True, 0, 0)
    reqHashBytes1 = addReqGetHashBytes(asc, req1)

    asc.r.newHashedReqUnveri(reqHashBytes1, {'from': asc.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callCancelHashedReqUnveri.encode_input(0, req1, *getIpfsMetaData(asc, req1))
    req2 = (asc.BOB.address, mockReentrancyAttack.address, asc.DENICE.address, callData, 0, 0, False, True)
    reqHashBytes2 = addReqGetHashBytes(asc, req2)

    asc.r.newHashedReqUnveri(reqHashBytes2, {'from': asc.BOB})

    with reverts(REV_MSG_REENTRANCY):
        asc.r.executeHashedReqUnveri(1, req2, *getIpfsMetaData(asc, req2))


def test_cancelHashedReqUnveri_no_ethForCall(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0
    tx = asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)

    # Should've changed
    reqHashesUnveri = [NULL_HASH]
    assert asc.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert asc.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert asc.r.getHashedReqsUnveriLen() == 1
    assert asc.r.getHashedReqUnveri(0) == NULL_HASH
    assert tx.events["HashedReqUnveriRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL

    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0


    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_cancelHashedReqUnveri_rev_req_not_the_same(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    # Alter the request
    invalidReq = list(req)
    invalidReq[6] = 1
    id = 0

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, invalidReq, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_already_executed(asc, stakedMin, mockTarget, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    id = 0
    asc.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_BOB)


def test_cancelHashedReqUnveri_rev_not_the_requester(asc, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0

    with reverts(REV_MSG_NOT_REQUESTER):
        asc.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(asc, req), asc.FR_ALICE)