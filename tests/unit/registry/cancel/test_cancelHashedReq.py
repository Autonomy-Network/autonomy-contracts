from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls callCancelHashedReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call callCancelHashedReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_cancelHashedReq_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE, callData, False, False, True, 0, 0)
    addToIpfs(auto, req1)

    auto.r.newReq(mockTarget, auto.DENICE, callData, 0, False, False, True, {'from': auto.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callCancelHashedReq.encode_input(0, req1)
    req2 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE, callData, 0, 0, False, False, True)
    addToIpfs(auto, req2)

    auto.r.newReq(mockReentrancyAttack, auto.DENICE, callData, 0, False, False, True, {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeHashedReq(1, req2, MIN_GAS)


def test_cancelHashedReq_no_ethForCall(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    tx = auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 8
    for i, reqHash in enumerate(reqHashes):
        assert auto.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (5 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReq_with_ethForCall(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1

    tx = auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 8
    for i, reqHash in enumerate(reqHashes):
        assert auto.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (5 * ethForCall) + msgValue

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReq_payAUTO(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2

    tx = auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 8
    for i, reqHash in enumerate(reqHashes):
        assert auto.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (5 * ethForCall)
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReq_pay_AUTO_with_ethForCall(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3

    tx = auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 8
    for i, reqHash in enumerate(reqHashes):
        assert auto.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (5 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReq_pay_AUTO_with_ethForCall_and_verifySender(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 4

    tx = auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)

    # Should've changed
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 8
    for i, reqHash in enumerate(reqHashes):
        assert auto.r.getHashedReq(i) == reqHash
    assert tx.events["HashedReqRemoved"][0].values() == [id, False]
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (5 * ethForCall) + ethForCall

    # Shouldn't've changed
    assert mockTarget.x() == 0
    assert mockTarget.userAddr() == ADDR_0
    assert mockTarget.msgSender() == ADDR_0

    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL

    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0


    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_cancelHashedReq_rev_req_not_the_same(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1

    with reverts(REV_MSG_NOT_SAME):
        auto.r.cancelHashedReq(id, reqs[2], auto.FR_BOB)


def test_cancelHashedReq_rev_already_executed(auto, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1
    # expectedGas = auto.r.executeHashedReq.call(id, reqs[id], 0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    auto.r.executeHashedReq(id, reqs[id], 0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME):
        auto.r.cancelHashedReq(id, reqs[id], auto.FR_BOB)


def test_cancelHashedReq_rev_not_the_requester(auto, stakedMin, mockTarget, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    id = 1

    with reverts(REV_MSG_NOT_REQUESTER):
        auto.r.cancelHashedReq(id, reqs[id], auto.FR_ALICE)