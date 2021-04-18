from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


# Making a request that calls executeHashedReq should be banned to reduce attack surface
# and generally prevent unknown funny business. Any 'legitimate' use of ASC should
# just make a new request for recursive ASCs, I see no reason to need to call executeHashedReq
# from a request etc. Can't make a call directly to the registry from the registry
# because of `targetNotThis`, so need to call into it from a new contract
def test_executeHashedReq_rev_nonReentrant(asc, mockTarget, mockReentrancyAttack):
    # Create request to call in reentrance
    callData = mockTarget.setX.encode_input(5)
    req1 = (asc.BOB.address, mockReentrancyAttack.address, callData, False, True, 0, 0, asc.DENICE.address)
    addToIpfs(asc, req1)

    asc.r.newHashedReq(mockTarget, callData, False, True, 0, asc.DENICE, *getIpfsMetaData(asc, req1), {'from': asc.BOB})

    # Create request to be executed directly
    callData = mockReentrancyAttack.callExecuteHashedReq.encode_input(0, req1, *getIpfsMetaData(asc, req1))
    req2 = (asc.BOB.address, mockReentrancyAttack.address, callData, False, True, 0, 0, asc.DENICE.address)
    addToIpfs(asc, req2)

    asc.r.newHashedReq(mockReentrancyAttack, callData, False, True, 0, asc.DENICE, *getIpfsMetaData(asc, req2), {'from': asc.BOB})

    with reverts(REV_MSG_REENTRANCY):
        asc.r.executeHashedReq(1, req2, *getIpfsMetaData(asc, req2))


# Randomly generate addresses for the sender and calldata input independently
# to test validCalldata upon calling executeHashedReq
@given(
    ethForCall=strategy('uint256', max_value=E_18),
    payWithASC=strategy('bool'),
    userAddr=strategy('address'),
    sender=strategy('address')
)
def test_executeHashedReq_validCalldata(asc, stakedMin, mockTarget, ethForCall, payWithASC, userAddr, sender):
    # It's gonna be a pain in the ass to do the accounting if they're equal
    if sender != asc.ALICE and sender != asc.DENICE:
        _, staker, __ = stakedMin

        msgValue = ethForCall + E_18
        if payWithASC:
            msgValue = ethForCall

        id = 0
        callData = mockTarget.setAddrPayVerified.encode_input(userAddr)
        req = (sender.address, mockTarget.address, callData, True, payWithASC, msgValue, ethForCall, asc.DENICE.address)
        addToIpfs(asc, req)

        asc.ASC.approve(asc.r, MAX_TEST_STAKE, {'from': sender})
        asc.ASC.transfer(sender, MAX_TEST_STAKE, asc.FR_DEPLOYER)
        senderASCStartBal = asc.ASC.balanceOf(sender)
        asc.r.newHashedReq(mockTarget, callData, True, payWithASC, ethForCall, asc.DENICE, *getIpfsMetaData(asc, req), {'from': sender, 'value': msgValue})

        if userAddr != sender:
            with reverts(REV_MSG_CALLDATA_NOT_VER):
                asc.r.executeHashedReq(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
        else:
            tx = asc.r.executeHashedReq(id, req, *getIpfsMetaData(asc, req), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

            assert mockTarget.balance() == ethForCall
            if payWithASC:
                # Eth bals
                assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall
                # ASC bals
                ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
                assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
                assert asc.ASC.balanceOf(sender) - senderASCStartBal == -ASCForExec
                assert asc.ASC.balanceOf(asc.DENICE) == 0
                assert asc.ASC.balanceOf(asc.r) == 0
            else:
                # Eth bals
                ethForExec = getEthForExec(tx, INIT_ETH_PER_USD)
                assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
                assert sender.balance() == INIT_ETH_BAL - ethForCall - ethForExec
                # ASC bals
                assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
                assert asc.ASC.balanceOf(sender) - senderASCStartBal == 0
                assert asc.ASC.balanceOf(asc.DENICE) == 0
                assert asc.ASC.balanceOf(asc.r) == 0

            # Target state
            assert mockTarget.userAddr() == sender.address
            assert mockTarget.msgSender() == asc.vf.address
            # Registry state
            reqHashes = [NULL_HASH]
            assert asc.r.getHashedReqs() == reqHashes
            # Should revert when using indexes above the length
            with reverts():
                asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
            assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
            assert asc.r.getHashedReqsLen() == 1
            assert asc.r.getHashedReq(id) == NULL_HASH
            assert tx.events["HashedReqRemoved"][0].values() == [id, True]
            assert asc.r.getReqCountOf(sender) == 1
            assert asc.r.getExecCountOf(asc.ALICE) == 1
            assert asc.r.getReferalCountOf(asc.DENICE) == 1

            # Shouldn't've changed
            assert mockTarget.x() == 0
            assert asc.r.balance() == 0
        
                

def test_executeHashedReq_no_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 0
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_ETH_PER_USD)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeHashedReq_with_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 1
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    ethForExec = getEthForExec(tx, INIT_ETH_PER_USD)
    assert asc.ALICE.balance() == INIT_ETH_BAL + ethForExec - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall)) + msgValue - ethForCall - ethForExec
    assert asc.r.balance() == msgValue + (2 * ethForCall)
    assert mockTarget.balance() == ethForCall
    # ASC bals
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqHashes[id] = NULL_HASH
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeHashedReq_pay_ASC(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 2
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == (2 * msgValue) + (2 * ethForCall)
    assert mockTarget.balance() == 0
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeHashedReq_pay_ASC_with_ethForCall(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 3
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.x() == 5
    assert mockTarget.msgSender() == asc.r
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.userAddr() == ADDR_0



def test_executeHashedReq_pay_ASC_with_ethForCall_and_verifySender(asc, stakedMin, mockTarget, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    # reqHashes will modify the original even after this test has finished otherwise since it's a reference
    reqHashes = reqHashes[:]
    id = 4
    assert mockTarget.x() == 0
    assert asc.ALICE.balance() == INIT_ETH_BAL
    assert asc.BOB.balance() == INIT_ETH_BAL - (2 * msgValue) - (2 * ethForCall)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    tx = asc.r.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})
    
    # Should've changed
    # Eth bals
    assert asc.ALICE.balance() == INIT_ETH_BAL - (tx.gas_used * tx.gas_price)
    assert asc.BOB.balance() == INIT_ETH_BAL - ((2 * msgValue) + (2 * ethForCall))
    assert asc.r.balance() == 2 * msgValue + ethForCall
    assert mockTarget.balance() == ethForCall
    # ASC bals
    ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
    assert asc.ASC.balanceOf(asc.ALICE) == MAX_TEST_STAKE - STAN_STAKE + ASCForExec
    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE - ASCForExec
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(asc.r) == 0
    # Target state
    assert mockTarget.userAddr() == asc.BOB.address
    assert mockTarget.msgSender() == asc.vf.address
    # Registry state
    reqHashes[id] = NULL_HASH
    assert asc.r.getHashedReqs() == reqHashes
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, len(reqHashes) + 1)
    assert asc.r.getHashedReqsSlice(0, len(reqHashes)) == reqHashes
    assert asc.r.getHashedReqsLen() == 5
    assert asc.r.getHashedReq(id) == NULL_HASH
    assert tx.events["HashedReqRemoved"][0].values() == [id, True]
    assert asc.r.getReqCountOf(asc.BOB) == 1
    assert asc.r.getExecCountOf(asc.ALICE) == 1
    assert asc.r.getReferalCountOf(asc.DENICE) == 1

    # Shouldn't've changed
    assert mockTarget.x() == 0


def test_executeHashedReq_rev_not_executor(asc, stakedMin, hashedReqs):
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    with reverts(REV_MSG_NOT_EXEC):
        asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': asc.DENICE, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_req_not_the_same(asc, stakedMin, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs
    invalidReq = list(reqs[0])
    invalidReq[6] = 1
    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReq(0, invalidReq, *getIpfsMetaData(asc, invalidReq), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_already_executeHashedReqd(asc, stakedMin, hashedReqs):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = hashedReqs

    asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})

    with reverts(REV_MSG_NOT_SAME):
        asc.r.executeHashedReq(0, reqs[0], *getIpfsMetaData(asc, reqs[0]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_noFish_pay_eth(asc, vulnerableRegistry, vulnerableHashedReqs, stakedMin):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = vulnerableHashedReqs
    id = 0

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})


def test_executeHashedReq_rev_noFish_payWithASC(asc, vulnerableRegistry, vulnerableHashedReqs, stakedMin):
    _, staker, __ = stakedMin
    reqs, reqHashes, msgValue, ethForCall = vulnerableHashedReqs
    id = 1

    with reverts(REV_MSG_FISHY):
        vulnerableRegistry.executeHashedReq(id, reqs[id], *getIpfsMetaData(asc, reqs[id]), {'from': staker, 'gasPrice': TEST_GAS_PRICE})