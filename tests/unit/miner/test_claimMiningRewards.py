from consts import *
from brownie.test import given, strategy
from brownie import a, reverts


@given(
    referer=strategy('address'),
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address')
)
def test_claimMiningRewards_requester(auto, mockTarget, referer, ethForCall, requester, executor):
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

        auto.m.claimMiningRewards({'from': requester})
        
        # Should've changed
        rewardAmount = ((reqCount[requester] * INIT_REQUESTER_REWARD) +
            (execCount[requester] * INIT_EXECUTOR_REWARD) +
            (referalCount[requester] * INIT_REFERAL_REWARD))
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL - rewardAmount
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == requester else (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) +
                    (execCount[addr] * INIT_EXECUTOR_REWARD) +
                    (referalCount[addr] * INIT_REFERAL_REWARD)
            )
            assert auto.m.getMinedReqCountOf(addr) == (1 if addr == requester else 0)
            assert auto.m.getMinedExecCountOf(addr) == (1 if addr == requester and requester == executor else 0)
            assert auto.m.getMinedReferalCountOf(addr) == (1 if addr == requester and requester == referer else 0)
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == requester else 0)
        
        # Shouldn't've changed
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


@given(
    referer=strategy('address'),
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address')
)
def test_claimMiningRewards_executor(auto, mockTarget, referer, ethForCall, requester, executor):
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

        auto.m.claimMiningRewards({'from': executor})
        
        # Should've changed
        rewardAmount = ((reqCount[executor] * INIT_REQUESTER_REWARD) +
            (execCount[executor] * INIT_EXECUTOR_REWARD) +
            (referalCount[executor] * INIT_REFERAL_REWARD))
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL - rewardAmount
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == executor else (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) +
                    (execCount[addr] * INIT_EXECUTOR_REWARD) +
                    (referalCount[addr] * INIT_REFERAL_REWARD)
            )
            assert auto.m.getMinedReqCountOf(addr) == (1 if addr == executor and executor == requester else 0)
            assert auto.m.getMinedExecCountOf(addr) == (1 if addr == executor else 0)
            assert auto.m.getMinedReferalCountOf(addr) == (1 if addr == executor and executor == referer else 0)
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == executor else 0)
        
        # Shouldn't've changed
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


@given(
    referer=strategy('address'),
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address')
)
def test_claimMiningRewards_referer(auto, mockTarget, referer, ethForCall, requester, executor):
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

        auto.m.claimMiningRewards({'from': referer})
        
        # Should've changed
        rewardAmount = ((reqCount[referer] * INIT_REQUESTER_REWARD) +
            (execCount[referer] * INIT_EXECUTOR_REWARD) +
            (referalCount[referer] * INIT_REFERAL_REWARD))
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL - rewardAmount
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0) if addr == referer else (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) +
                    (execCount[addr] * INIT_EXECUTOR_REWARD) +
                    (referalCount[addr] * INIT_REFERAL_REWARD)
            )
            assert auto.m.getMinedReqCountOf(addr) == (1 if addr == referer and referer == requester else 0)
            assert auto.m.getMinedExecCountOf(addr) == (1 if addr == referer and referer == executor else 0)
            assert auto.m.getMinedReferalCountOf(addr) == (1 if addr == referer else 0)
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == (rewardAmount if addr == referer else 0)
        
        # Shouldn't've changed
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


def test_claimMiningRewards_rev_no_pending_rewards(a, auto):
    for sender in a:
        with reverts(REV_MSG_NO_PEND_REW):
            auto.m.claimMiningRewards({'from': sender})