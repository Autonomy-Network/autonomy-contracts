from consts import *
from brownie.test import given, strategy


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address')
)
def test_getAvailableMiningRewards(asc, mockTarget, ethForCall, requester):
    if requester != asc.ALICE and requester != asc.DENICE:
        startBals = {}
        for addr in [requester, asc.ALICE, asc.DENICE]:
            assert asc.m.getMinedReqCountOf(addr) == 0
            assert asc.m.getMinedExecCountOf(addr) == 0
            assert asc.m.getMinedReferalCountOf(addr) == 0
            assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
            startBals[addr] = asc.ASC.balanceOf(addr)
        
        callData = mockTarget.setAddrPayVerified.encode_input(requester)
        msgValue = ethForCall + int(0.5 * E_18)
        asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, asc.DENICE, {'from': requester, 'value': msgValue})
        asc.r.executeRawReq(0, asc.FR_ALICE)

        # Should've changed
        assert asc.m.getAvailableMiningRewards(requester) == (1, 0, 0, INIT_REQUESTER_REWARD)
        assert asc.m.getAvailableMiningRewards(asc.ALICE) == (0, 1, 0, INIT_EXECUTOR_REWARD)
        assert asc.m.getAvailableMiningRewards(asc.DENICE) == (0, 0, 1, INIT_REFERAL_REWARD)


        # Shouldn't've changed
        for addr in [requester, asc.ALICE, asc.DENICE]:
            assert asc.m.getMinedReqCountOf(addr) == 0
            assert asc.m.getMinedExecCountOf(addr) == 0
            assert asc.m.getMinedReferalCountOf(addr) == 0
            assert asc.ASC.balanceOf(addr) - startBals[addr] == 0
        
        assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL
        assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
        assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
        assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


@given(
    ethForCall=strategy('uint256', max_value=E_18),
    requester=strategy('address'),
    executor=strategy('address'),
    referer=strategy('address')
)
def test_getAvailableMiningRewards_all_parties_random(asc, mockTarget, ethForCall, requester, executor, referer):
    addrs = [requester, executor, referer]
    reqCount = {addr: 1 if addr == requester else 0 for addr in addrs}
    execCount = {addr: 1 if addr == executor else 0 for addr in addrs}
    referalCount = {addr: 1 if addr == referer else 0 for addr in addrs}

    startBals = {addr: asc.ASC.balanceOf(addr) for addr in addrs}
    for addr in addrs:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)
    
    callData = mockTarget.setAddrPayVerified.encode_input(requester)
    msgValue = ethForCall + int(0.5 * E_18)
    asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, referer, {'from': requester, 'value': msgValue})
    asc.r.executeRawReq(0, {'from': executor})

    # Should've changed
    for addr in addrs:
        assert asc.m.getAvailableMiningRewards(addr) == (
            reqCount[addr],
            execCount[addr],
            referalCount[addr],
            (reqCount[addr] * INIT_REQUESTER_REWARD) + (execCount[addr] * INIT_EXECUTOR_REWARD) + (referalCount[addr] * INIT_REFERAL_REWARD)
        )

    # Shouldn't've changed
    for addr in addrs:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.ASC.balanceOf(addr) - startBals[addr] == 0
    
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD


def test_getAvailableMiningRewards_requester_executor_referer_same(asc, mockTarget):
    assert asc.m.getMinedReqCountOf(asc.ALICE) == 0
    assert asc.m.getMinedExecCountOf(asc.ALICE) == 0
    assert asc.m.getMinedReferalCountOf(asc.ALICE) == 0
    assert asc.m.getAvailableMiningRewards(asc.ALICE) == (0, 0, 0, 0)
    startBal = asc.ASC.balanceOf(asc.ALICE)
    
    callData = mockTarget.setAddrPayVerified.encode_input(asc.ALICE)
    ethForCall = 0
    msgValue = E_18
    asc.ASC.approve(asc.r, MAX_TEST_STAKE, {'from': asc.ALICE})
    asc.r.newRawReq(mockTarget, callData, True, False, ethForCall, asc.ALICE, {'from': asc.ALICE, 'value': msgValue})
    asc.r.executeRawReq(0, asc.FR_ALICE)

    # Should've changed
    assert asc.m.getAvailableMiningRewards(asc.ALICE) == (1, 1, 1, INIT_REQUESTER_REWARD + INIT_EXECUTOR_REWARD + INIT_REFERAL_REWARD)

    # Shouldn't've changed
    assert asc.m.getMinedReqCountOf(asc.ALICE) == 0
    assert asc.m.getMinedExecCountOf(asc.ALICE) == 0
    assert asc.m.getMinedReferalCountOf(asc.ALICE) == 0
    assert asc.ASC.balanceOf(asc.ALICE) - startBal == 0
    
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD