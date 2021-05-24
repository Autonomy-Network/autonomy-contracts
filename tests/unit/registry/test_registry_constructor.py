from consts import *
from brownie import reverts


def test_constructor(asc):
    assert asc.r.getASCoin() == asc.ASC
    assert asc.r.GAS_OVERHEAD_ASCOIN() == GAS_OVERHEAD_ASCOIN
    assert asc.r.GAS_OVERHEAD_ETH() == GAS_OVERHEAD_ETH
    assert asc.r.BASE_BPS() == BASE_BPS
    assert asc.r.PAY_AUTO_BPS() == PAY_AUTO_BPS
    assert asc.r.PAY_ETH_BPS() == PAY_ETH_BPS
    assert asc.r.getASCoin() == asc.ASC
    assert asc.r.getStakeManager() == asc.sm

    assert asc.r.getRawReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getRawReqsSlice(0, 1)
    assert asc.r.getRawReqsSlice(0, 0) == []
    assert asc.r.getRawReqLen() == 0
    with reverts():
        assert asc.r.getRawReq(0)
    
    assert asc.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsSlice(0, 1)
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)
    
    assert asc.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        asc.r.getHashedReqsUnveriSlice(0, 1)
    assert asc.r.getHashedReqsUnveriSlice(0, 0) == []
    assert asc.r.getHashedReqsUnveriLen() == 0
    with reverts():
        asc.r.getHashedReqUnveri(0)
    