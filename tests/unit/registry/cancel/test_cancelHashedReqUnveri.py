from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeHashedReqUnveri should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call executeHashedReqUnveri
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_cancelHashedReqUnveri_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (auto.BOB.address, mockTarget.address, auto.DENICE.address, callData, False, False, True, False, 0, 0)
    reqHashBytes1 = addReqGetHashBytes(auto, req1)

    auto.r.newHashedReqUnveri(reqHashBytes1, {'from': auto.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callCancelHashedReqUnveri.encode_input(0, req1, *getIpfsMetaData(auto, req1))
    req2 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE.address, callData, 0, 0, False, False, True, False)
    reqHashBytes2 = addReqGetHashBytes(auto, req2)

    auto.r.newHashedReqUnveri(reqHashBytes2, {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeHashedReqUnveri(1, req2, *getIpfsMetaData(auto, req2), MIN_GAS)


def test_cancelHashedReqUnveri_no_ethForCall(auto, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0
    tx = auto.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), auto.FR_BOB)

    # Should've changed
    reqHashesUnveri = [NULL_HASH]
    assert auto.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert auto.r.getHashedReqsUnveriLen() == 1
    assert auto.r.getHashedReqUnveri(0) == NULL_HASH
    assert tx.events["HashedReqUnveriCancelled"][0].values() == [id]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReqUnveri_rev_req_not_the_same(auto, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    # Alter the request
    invalidReq = list(req)
    invalidReq[6] = 1
    id = 0

    with reverts(REV_MSG_NOT_SAME_IPFS):
        auto.r.cancelHashedReqUnveri(id, invalidReq, *getIpfsMetaData(auto, req), auto.FR_BOB)


def test_cancelHashedReqUnveri_rev_already_executed(auto, stakedMin, mockTarget, hashedReqUnveri):
    _, staker, __ = stakedMin
    req, reqHashBytes = hashedReqUnveri
    id = 0
    expectedGas = auto.r.executeHashedReqUnveri.call(id, req, *getIpfsMetaData(auto, req), 0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    auto.r.executeHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), expectedGas, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME_IPFS):
        auto.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), auto.FR_BOB)


def test_cancelHashedReqUnveri_rev_not_the_requester(auto, stakedMin, mockTarget, hashedReqUnveri):
    req, reqHashBytes = hashedReqUnveri
    id = 0

    with reverts(REV_MSG_NOT_REQUESTER):
        auto.r.cancelHashedReqUnveri(id, req, *getIpfsMetaData(auto, req), auto.FR_ALICE)