from consts import *
from brownie import reverts


def test_constructor(asc):
    assert asc.r.getASCoin() == asc.ASCoin
    # assert asc.r.EXEC_GAS_OVERHEAD_NO_REF() == EXEC_GAS_OVERHEAD_NO_REF
    # assert asc.r.EXEC_GAS_OVERHEAD_REF() == EXEC_GAS_OVERHEAD_REF
    assert asc.r.GAS_OVERHEAD_ETH() == GAS_OVERHEAD_ETH
    assert asc.r.GAS_OVERHEAD_ASCOIN() == GAS_OVERHEAD_ASCOIN
    assert asc.r.owner() == asc.DEPLOYER
    assert asc.r.getASCoin() == asc.ASCoin
    assert asc.r.getStakeManager() == asc.sm
    assert asc.r.getRequests() == []
    assert asc.r.getRequestsLength() == 0
    with reverts():
        assert asc.r.getRequest(0)
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getEthToASCoinRate() == INIT_ETH_TO_ASCOIN_RATE
    assert asc.r.getCumulRewardsOf(asc.DEPLOYER) == 0