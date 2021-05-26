from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeHashedReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of AUTO should
# just make a new request for recursive requests, I see no reason to need to call executeHashedReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeHashedReq_rev_nonReentrant(auto, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE, callData, 0, 0, False, True)
    addToIpfs(auto, req1)

    auto.r.newHashedReq(mockTarget, auto.DENICE, callData, 0, False, True, *getIpfsMetaData(auto, req1), {'from': auto.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteHashedReq.encode_input(0, req1, *getIpfsMetaData(auto, req1))
    req2 = (auto.BOB.address, mockReentrancyAttack.address, auto.DENICE, callData, 0, 0, False, True)
    addToIpfs(auto, req2)

    auto.r.newHashedReq(mockReentrancyAttack, auto.DENICE, callData, 0, False, True, *getIpfsMetaData(auto, req2), {'from': auto.BOB})

    with reverts(REV_MSG_REENTRANCY):
        auto.r.executeHashedReq(1, req2, *getIpfsMetaData(auto, req2))


# Check that the revert message from the target contract is passed on correctly
def test_executeHashedReq_returns_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin
    
    callData = mockTarget.revertWithMessage.encode_input()
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, E_18, 0, False, False)
    tx = auto.r.newHashedReq(mockTarget, auto.DENICE, callData, 0, False, False, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

    with reverts(REV_MSG_GOOFED):
        auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


# Check that no revert message from the target contract is passed on correctly
def test_executeHashedReq_returns_no_revert_message(auto, stakedMin, mockTarget):
    _, staker, __ = stakedMin
    
    callData = mockTarget.revertWithoutMessage.encode_input()
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, E_18, 0, False, False)
    tx = auto.r.newHashedReq(mockTarget, auto.DENICE, callData, 0, False, False, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

    with reverts(''):
        auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


# Randomly generate addresses for the sender and calldata input independently
# to test validCalldata upon calling executeHashedReq
@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithAUTO=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_executeHashedReq_validCalldata(auto, evmMaths, stakedMin, mockTarget, ethForCall, payWithAUTO, userAddr, sender):
    # It's gonna be a pain in the ass to do the accounting if they're equal
    if sender != auto.ALICE and sender != auto.DENICE:
        _, staker, __ = stakedMin

        msgValue = ethForCall + E_18
        if payWithAUTO:
            msgValue = ethForCall

        id = 0
        callData = mockTarget.setAddrPayVerified.encode_input(userAddr)
        req = (sender.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, True, payWithAUTO)
        addToIpfs(auto, req)

        auto.AUTO.approve(auto.r, MAX_TEST_STAKE, {'from': sender})
        auto.AUTO.transfer(sender, MAX_TEST_STAKE, auto.FR_DEPLOYER)
        senderAUTOStartBal = auto.AUTO.balanceOf(sender)
        auto.r.newHashedReq(mockTarget, auto.DENICE, callData, ethForCall, True, payWithAUTO, *getIpfsMetaData(auto, req), {'from': sender, 'value': msgValue})

        if userAddr != sender:
            with reverts(REV_MSG_CALLDATA_NOT_VER):
                auto.r.executeHashedReq(id, req, *getIpfsMetaData(auto, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
        else:
            tx = auto.r.executeHashedReq(id, req, *getIpfsMetaData(auto, req), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

            assert mockTarget.balance() == ethForCall
            if payWithAUTO:
                # Eth bals
                assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall
                # AUTO bals
                AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
                assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
                assert auto.AUTO.balanceOf(sender) - senderAUTOStartBal == -AUTOForExec
                assert auto.AUTO.balanceOf(auto.DENICE) == 0
                assert auto.AUTO.balanceOf(auto.r) == 0
            else:
                # Eth bals
                ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
                assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall - ethForExec
                # AUTO bals
                assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
                assert auto.AUTO.balanceOf(sender) - senderAUTOStartBal == 0
                assert auto.AUTO.balanceOf(auto.DENICE) == 0
                assert auto.AUTO.balanceOf(auto.r) == 0

            # Target state
            assert mockTarget.userAddr() == sender.address
            assert mockTarget.msgSender() == auto.vf.address
            # Registry state
            reqHashes = [NULL_HASH]
            assert auto.r.getHashedReqs() == reqHashes
            # Should revert when using indexes above the length
            with reverts():
                auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
            assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
            assert auto.r.getHashedReqsLen() == 1
            assert auto.r.getHashedReq(id) == NULL_HASH
            assert tx.events["HashedReqRemoved"][0].values() == [id, True]
            assert auto.r.getReqCountOf(sender) == 1
            assert auto.r.getExecCountOf(auto.ALICE) == 1
            assert auto.r.getReferalCountOf(auto.DENICE) == 1

            # Shouldn't've changed
            assert mockTarget.x() == 0
            assert auto.r.balance() == 0


def test_executeHashedReq_no_ethForCall(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
    assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForExec
    assert auto.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 5
    assert auto.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReq_with_ethForCall(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
    assert auto.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForCall - ethForExec
    assert auto.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqHashes[id] = NULL_HASH
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 5
    assert auto.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReq_pay_AUTO(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 5
    assert auto.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReq_pay_AUTO_with_ethForCall(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == auto.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 5
    assert auto.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0


def test_executeHashedReq_pay_AUTO_with_ethForCall_and_verifySender(auto, evmMaths, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 4
    assert mockTarget.x() == 0
    assert auto.ALICE.balance() == INIT_ETH_BAL
    assert auto.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    tx = auto.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Should've changed
    # Eth bals
    assert auto.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert auto.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert auto.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # AUTO bals
    AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    assert auto.AUTO.balanceOf(auto.ALICE) == MAX_TEST_STAKE - STAN_STAKE + AUTOForExec
    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE - AUTOForExec
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0
    # Target state
    assert mockTarget.userAddr() == auto.BOB.address
    assert mockTarget.msgSender() == auto.vf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert auto.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert auto.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert auto.r.getHashedReqsLen() == 5
    assert auto.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert auto.r.getReqCountOf(auto.BOB) == 1
    assert auto.r.getExecCountOf(auto.ALICE) == 1
    assert auto.r.getReferalCountOf(auto.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.x() == 0


def test_executeHashedReq_rev_not_executor(auto, stakedMin, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    with reverts(REV_MSG_NOT_EXEC):
        auto.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(auto, reqs[0]), {'from': auto.DENICE, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReq_rev_req_not_the_same(auto, stakedMin, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    invalidReq = list(reqs[0])
    invalidReq[4] = 1
    with reverts(REV_MSG_NOT_SAME):
        auto.r.executeHashedReq(0, invalidReq, *getIpfsMetaData(auto, invalidReq), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReq_rev_already_executeHashedReqd(auto, stakedMin, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs

    auto.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(auto, reqs[0]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})

    with reverts(REV_MSG_NOT_SAME):
        auto.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(auto, reqs[0]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReq_rev_noFish_pay_eth(auto, vulnerableRegistry, vulnerableHashedReqs, stakedMin):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = vulnerableHashedReqs
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})


def test_executeHashedReq_rev_noFish_payWithAUTO(auto, vulnerableRegistry, vulnerableHashedReqs, stakedMin):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = vulnerableHashedReqs
    id = 1

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReq(id, reqs[id], *getIpfsMetaData(auto, reqs[id]), {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})