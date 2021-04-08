from consts import *
from brownie.test import given, strategy
from brownie import reverts


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address')
)
def test_claimExecMiningReward(asc, mockTarget, ethForCall, requester):
    if requester != asc.ALICE and requester != asc.DENICE:
        addrs = [requester, asc.ALICE, asc.DENICE]
        for addr in addrs:
            assert asc.m.getMinedReqCountOf(addr) == 0
            assert asc.m.getMinedExecCountOf(addr) == 0
            assert asc.m.getMinedReferalCountOf(addr) == 0
            assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
        
        callData = mockTarget.setAddrPayVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, asc.DENICE, {'from': requester, 'value': msgValue})
        asc.r.executeRawReq(0, asc.FR_ALICE)

        startBals = {addr: asc.ASC.balanceOf(addr) for addr in addrs}
        # Should've changed
        for addr in addrs:
            assert asc.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
            assert asc.m.getAvailableMiningRewards(asc.ALICE) == (0, 1, 0, INIT_EXECUTOR_REWARD)
            assert asc.m.getAvailableMiningRewards(asc.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)

        # Shouldn't've changed
        for addr in addrs:
            assert asc.m.getMinedReqCountOf(addr) == 0
            assert asc.m.getMinedExecCountOf(addr) == 0
            assert asc.m.getMinedReferalCountOf(addr) == 0
            assert asc.ASC.balanceOf(addr) - startBals[addr] == 0

        asc.m.claimExecMiningReward(1, asc.FR_ALICE)
        
        # Should've changed
        assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL - INIT_EXECUTOR_REWARD
        for addr in addrs:
            assert asc.m.getAvailableMiningRewards(asc.ALICE) == (0, 0, 0, 0)
            assert asc.ASC.balanceOf(addr) - startBals[addr] == (INIT_EXECUTOR_REWARD if addr == asc.ALICE else 0)
        
        # Shouldn't've changed
        assert asc.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
        assert asc.m.getAvailableMiningRewards(asc.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)
        assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
        assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
        assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address'),
    referer=strategy('address')
)
def test_claimExecMiningReward_all_parties_random(asc, mockTarget, ethForCall, requester, executor, referer):
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

    asc.m.claimExecMiningReward(1, {'from': executor})
    # I guess this now measures the net difference between the counter in Registry and
    # the counter for how many counts have been claimed/mined in Miner
    execCount[executor] -= 1
    
    # Should've changed
    rewardAmount = INIT_EXECUTOR_REWARD
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL - INIT_EXECUTOR_REWARD
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) +
                (execCount[addr] * INIT_EXECUTOR_REWARD) +
                (referalCount[addr] * INIT_REFERAL_REWARD)
        )
        assert asc.ASC.balanceOf(addr) - startBals[addr] == (INIT_EXECUTOR_REWARD if addr == executor else 0)
    
    # Shouldn't've changed
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


@given(
    sender=strategy('address'),
    claimAmount=strategy('uint', exclude=0)
)
def test_claimExecMiningReward_rev_claimAmount(asc, sender, claimAmount):
    with reverts(REV_MSG_CLAIM_TOO_LARGE):
        asc.m.claimExecMiningReward(claimAmount, {'from': sender})