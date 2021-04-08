from consts import *
from brownie.test import given, strategy
from brownie import reverts


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address'),
    referer=strategy('address')
)
def test_claimMiningRewards_requester(asc, mockTarget, ethForCall, requester, executor, referer):
    addrs = [requester, executor, referer]
    reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
    execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
    referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}
    
    callData = mockTarget.setAddrPayVerified.encode_input(requester)
    msgValue = ethForCall + int(0.5 * E_18)
    asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, referer, {'from': requester, 'value': msgValue})
    asc.r.executeRawReq(0, {'from': executor})

    startBals = {addr: asc.ASC.balanceOf(addr) for addr in addrs}
    # Should've changed
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )

    # Shouldn't've changed
    for addr in addrs:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.ASC.balanceOf(addr) - startBals[addr] == 0

    asc.m.claimMiningRewards({'from': requester})
    
    # Should've changed
    rewardAmount = ((reqCount[requester] * INIT_REQUESTER_REWARD) +
        (execCount[requester] * INIT_EXECUTOR_REWARD) +
        (referalCount[requester] * INIT_REFERAL_REWARD))
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL - rewardAmount
    for addr in addrs:
        print(addr)
        assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == requester else (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )
        assert asc.m.getMinedReqCountOf(addr) == (1 if addr == requester else 0)
        assert asc.m.getMinedExecCountOf(addr) == (1 if addr == requester and requester == executor else 0)
        assert asc.m.getMinedReferalCountOf(addr) == (1 if addr == requester and requester == referer else 0)
        assert asc.ASC.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == requester else 0)
    
    # Shouldn't've changed
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address'),
    referer=strategy('address')
)
def test_claimMiningRewards_executor(asc, mockTarget, ethForCall, requester, executor, referer):
    addrs = [requester, executor, referer]
    reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
    execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
    referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}
    
    callData = mockTarget.setAddrPayVerified.encode_input(requester)
    msgValue = ethForCall + int(0.5 * E_18)
    asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, referer, {'from': requester, 'value': msgValue})
    asc.r.executeRawReq(0, {'from': executor})

    startBals = {addr: asc.ASC.balanceOf(addr) for addr in addrs}
    # Should've changed
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )

    # Shouldn't've changed
    for addr in addrs:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.ASC.balanceOf(addr) - startBals[addr] == 0

    asc.m.claimMiningRewards({'from': executor})
    
    # Should've changed
    rewardAmount = ((reqCount[executor] * INIT_REQUESTER_REWARD) +
        (execCount[executor] * INIT_EXECUTOR_REWARD) +
        (referalCount[executor] * INIT_REFERAL_REWARD))
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL - rewardAmount
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == executor else (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )
        assert asc.m.getMinedReqCountOf(addr) == (1 if addr == executor and executor == requester else 0)
        assert asc.m.getMinedExecCountOf(addr) == (1 if addr == executor else 0)
        assert asc.m.getMinedReferalCountOf(addr) == (1 if addr == executor and executor == referer else 0)
        assert asc.ASC.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == executor else 0)
    
    # Shouldn't've changed
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address'),
    referer=strategy('address')
)
def test_claimMiningRewards_referer(asc, mockTarget, ethForCall, requester, executor, referer):
    addrs = [requester, executor, referer]
    reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
    execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
    referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}
    
    callData = mockTarget.setAddrPayVerified.encode_input(requester)
    msgValue = ethForCall + int(0.5 * E_18)
    asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, referer, {'from': requester, 'value': msgValue})
    asc.r.executeRawReq(0, {'from': executor})

    startBals = {addr: asc.ASC.balanceOf(addr) for addr in addrs}
    # Should've changed
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )

    # Shouldn't've changed
    for addr in addrs:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.ASC.balanceOf(addr) - startBals[addr] == 0

    asc.m.claimMiningRewards({'from': referer})
    
    # Should've changed
    rewardAmount = ((reqCount[referer] * INIT_REQUESTER_REWARD) +
        (execCount[referer] * INIT_EXECUTOR_REWARD) +
        (referalCount[referer] * INIT_REFERAL_REWARD))
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL - rewardAmount
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == referer else (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )
        assert asc.m.getMinedReqCountOf(addr) == (1 if addr == referer and referer == requester else 0)
        assert asc.m.getMinedExecCountOf(addr) == (1 if addr == referer and referer == executor else 0)
        assert asc.m.getMinedReferalCountOf(addr) == (1 if addr == referer else 0)
        assert asc.ASC.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == referer else 0)
    
    # Shouldn't've changed
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


def test_claimMiningRewards_rev_no_pending_rewards(a, asc):
    for sender in a:
        with reverts(REV_MSG_NO_PEND_REW):
            asc.m.claimMiningRewards({'from': sender})