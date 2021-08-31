from consts import *
from brownie.test import given, strategy


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address')
)
def test_getAvailableMiningRewards(auto, mockTarget, ethForCall, requester):
    if requester != auto.ALICE and requester != auto.DENICE and str(requester) in auto.EOAsStr:
        startBals = {}
        for addr in [requester, auto.ALICE, auto.DENICE]:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
            startBals[addr] = auto.AUTO.balanceOf(addr)
        
        callData = mockTarget.setAddrPayUserVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, True, False, False, False, {'from': requester, 'value': msgValue})
        req = (requester, mockTarget, auto.DENICE, callData, msgValue, ethForCall, True, False, False, False)
        auto.r.executeHashedReq(0, req, MIN_GAS, auto.FR_ALICE)

        # Should've changed
        assert auto.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
        assert auto.m.getAvailableMiningRewards(auto.ALICE) == (0, 1, 0, INIT_EXECUTOR_REWARD)
        assert auto.m.getAvailableMiningRewards(auto.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)


        # Shouldn't've changed
        for addr in [requester, auto.ALICE, auto.DENICE]:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == 0
        
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


@given(
    referer=strategy('address'),
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address')
)
def test_getAvailableMiningRewards_all_parties_random(auto, mockTarget, referer, ethForCall, requester, executor):
    if str(requester) in auto.EOAsStr:
        addrs = [requester, executor, referer]
        reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
        execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
        referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}

        startBals = {addr: auto.AUTO.balanceOf(addr) for addr in addrs}
        for addr in addrs:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
        
        callData = mockTarget.setAddrPayUserVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        auto.r.newReqPaySpecific(mockTarget, referer, callData, ethForCall, True, False, False, False, {'from': requester, 'value': msgValue})
        req = (requester, mockTarget, referer, callData, msgValue, ethForCall, True, False, False, False)
        auto.r.executeHashedReq(0, req, MIN_GAS, {'from': executor})

        # Should've changed
        for addr in addrs:
            assert auto.m.getAvailableMiningRewards(addr) == (
                reqCount[addr],
                execCount[addr],
                referalCount[addr],
                (reqCount[addr] * INIT_REQUESTER_REWARD) + (execCount[addr] * INIT_EXECUTOR_REWARD) + (referalCount[addr] * INIT_REFERAL_REWARD)
            )

        # Shouldn't've changed
        for addr in addrs:
            assert auto.m.getMinedReqCountOf(addr) == 0
            assert auto.m.getMinedExecCountOf(addr) == 0
            assert auto.m.getMinedReferalCountOf(addr) == 0
            assert auto.AUTO.balanceOf(addr) - startBals[addr] == 0
        
        assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL
        assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
        assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
        assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD


def test_getAvailableMiningRewards_requester_executor_referer_same(auto, mockTarget):
    assert auto.m.getMinedReqCountOf(auto.ALICE) == 0
    assert auto.m.getMinedExecCountOf(auto.ALICE) == 0
    assert auto.m.getMinedReferalCountOf(auto.ALICE) == 0
    assert auto.m.getAvailableMiningRewards(auto.ALICE) == (0, 0, 0, 0)
    startBal = auto.AUTO.balanceOf(auto.ALICE)
    
    callData = mockTarget.setAddrPayUserVerified.encode_input(auto.ALICE)
    ethForCall = 0
    msgValue = E_18
    auto.r.newReqPaySpecific(mockTarget, auto.ALICE, callData, ethForCall, True, False, False, False, {'from': auto.ALICE, 'value': msgValue})
    req = (auto.ALICE, mockTarget, auto.ALICE, callData, msgValue, ethForCall, True, False, False, False)
    auto.r.executeHashedReq(0, req, MIN_GAS, auto.FR_ALICE)

    # Should've changed
    assert auto.m.getAvailableMiningRewards(auto.ALICE) == (1, 1, 1, INIT_REQUESTER_REWARD + INIT_EXECUTOR_REWARD + INIT_REFERAL_REWARD)

    # Shouldn't've changed
    assert auto.m.getMinedReqCountOf(auto.ALICE) == 0
    assert auto.m.getMinedExecCountOf(auto.ALICE) == 0
    assert auto.m.getMinedReferalCountOf(auto.ALICE) == 0
    assert auto.AUTO.balanceOf(auto.ALICE) - startBal == 0
    
    assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL
    assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
    assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
    assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD