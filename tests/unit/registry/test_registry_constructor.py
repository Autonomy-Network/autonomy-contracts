from consts import *
from brownie import reverts


def test_constructor(asc):
    assert asc.r.getASCoin() == asc.ASC
    # assert asc.r.EXEC_GAS_OVERHEAD_NO_REF() == EXEC_GAS_OVERHEAD_NO_REF
    # assert asc.r.EXEC_GAS_OVERHEAD_REF() == EXEC_GAS_OVERHEAD_REF
    assert asc.r.GAS_OVERHEAD_ETH() == GAS_OVERHEAD_ETH
    assert asc.r.GAS_OVERHEAD_ASCOIN() == GAS_OVERHEAD_ASCOIN
    assert asc.r.getASCoin() == asc.ASC
    assert asc.r.getStakeManager() == asc.sm

    assert asc.r.getRawRequests() == []
    assert asc.r.getRawRequestsLen() == 0
    with reverts():
        assert asc.r.getRawRequest(0)
    
    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)
    
    assert asc.r.getHashedIpfsReqsNoEth() == []
    assert asc.r.getHashedIpfsReqsNoEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqNoEth(0)
    
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY
    assert asc.r.getRequesterReward() == INIT_REQUESTER_REWARD
    assert asc.r.getExecutorReward() == INIT_EXECUTOR_REWARD
    assert asc.r.getCumulRewardsOf(asc.DEPLOYER) == 0