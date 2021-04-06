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

    assert asc.r.getRawReqs() == []
    assert asc.r.getRawReqLen() == 0
    with reverts():
        assert asc.r.getRawReq(0)
    
    assert asc.r.getHashedReqs() == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)
    
    assert asc.r.getHashedReqsUnveri() == []
    assert asc.r.getHashedReqsUnveriLen() == 0
    with reverts():
        asc.r.getHashedReqUnveri(0)
    
    assert asc.r.getBaseBountyAsEth() == INIT_BASE_BOUNTY