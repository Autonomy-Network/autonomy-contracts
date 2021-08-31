from consts import *
from brownie.test import given, strategy
from brownie import reverts


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address')
)
def test_claimExecMiningReward(auto, mockTarget, ethForCall, requester):
    if requester != auto.ALICE and requester != auto.DENICE and str(requester) in auto.EOAsStr:
        addrs = [requester, auto.ALICE, auto.DENICE]
        for addr in addrs:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
        
        callData = mockTarget.setAddrPayUserVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, True, False, False, False, {'from': requester, 'value': msgValue})
        req = (requester, mockTarget, auto.DENICE, callData, msgValue, ethForCall, True, False, False, False)
        auto.r.executeHashedReq(0, req, MIN_GAS, auto.FR_ALICE)

        startBals = {addr: auto.AUTO.balanceOf(addr) for addr in addrs}
        # Should've changed
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
            assert auto.m.getAvailableMiningRewards(auto.ALICE) == (0, 1, 0, INIT_EXECUTOR_REWARD)
            assert auto.m.getAvailableMiningRewards(auto.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)

        # Shouldn't've changed
        for addr in addrs:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == 0

        auto.m.claimExecMiningReward(1, auto.FR_ALICE)
        
        # Should've changed
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL - INIT_EXECUTOR_REWARD
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(auto.ALICE) == (0, 0, 0, 0)
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == (INIT_EXECUTOR_REWARD if addr == auto.ALICE else 0)
        
        # Shouldn't've changed
        assert auto.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
        assert auto.m.getAvailableMiningRewards(auto.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


@given(
    referer=strategy('address'),
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address')
)
def test_claimExecMiningReward_all_parties_random(auto, mockTarget, referer, ethForCall, requester, executor):
    if str(requester) in auto.EOAsStr and str(executor) in auto.EOAsStr:
        addrs = [requester, executor, referer]
        reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
        execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
        referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}
        
        callData = mockTarget.setAddrPayUserVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        auto.r.newReqPaySpecific(mockTarget, referer, callData, ethForCall, True, False, False, False, {'from': requester, 'value': msgValue})
        req = (requester, mockTarget, referer, callData, msgValue, ethForCall, True, False, False, False)
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': executor})

        startBals = {addr: auto.AUTO.balanceOf(addr) for addr in addrs}
        # Should've changed
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) +
                    (execCount[addr] * INIT_EXECUTOR_REWARD) +
                    (referalCount[addr] * INIT_REFERAL_REWARD)
            )

        # Shouldn't've changed
        for addr in addrs:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == 0

        auto.m.claimExecMiningReward(1, {'from': executor})
        # I guess this now measures the net difference between the counter in Registry and
        # the counter for how many counts have been claimed/mined in Miner
        execCount[executor] -= 1
        
        # Should've changed
        rewardAmount = INIT_EXECUTOR_REWARD
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL - INIT_EXECUTOR_REWARD
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) +
                    (execCount[addr] * INIT_EXECUTOR_REWARD) +
                    (referalCount[addr] * INIT_REFERAL_REWARD)
            )
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == (INIT_EXECUTOR_REWARD if addr == executor else 0)
        
        # Shouldn't've changed
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


@given(
    sender=strategy('address'),
    claimAmount=strategy('uint', exclude=0)
)
def test_claimExecMiningReward_rev_claimAmount(auto, sender, claimAmount):
    with reverts(REV_MSG_CLAIM_TOO_LARGE):
        auto.m.claimExecMiningReward(claimAmount, {'from': sender})