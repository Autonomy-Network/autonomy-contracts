from consts import *


def test_constructor(asc):
    assert asc.r.ASCoin() == ASCOIN_ADDR
    assert asc.r.EXEC_GAS_OVERHEAD_NO_REF() == EXEC_GAS_OVERHEAD_NO_REF
    assert asc.r.EXEC_GAS_OVERHEAD_REF() == EXEC_GAS_OVERHEAD_REF
    assert asc.r.ETH_BOUNTY() == ETH_BOUNTY
    assert asc.r.getOwner() == asc.DEPLOYER
    assert asc.r.getNumRequests() == 0
    assert asc.r.getRequest(0) == NULL_REQ
    assert asc.r.getMaxRewardPerASC() == MAX_REW_PER_ASC
    assert asc.r.getStakeManager() == asc.sm