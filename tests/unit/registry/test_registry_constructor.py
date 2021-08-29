from consts import *
from brownie import reverts


def test_constructor(auto):
    assert auto.r.GAS_OVERHEAD_AUTO() == GAS_OVERHEAD_AUTO
    assert auto.r.GAS_OVERHEAD_ETH() == GAS_OVERHEAD_ETH
    assert auto.r.BASE_BPS() == BASE_BPS
    assert auto.r.PAY_AUTO_BPS() == PAY_AUTO_BPS
    assert auto.r.PAY_ETH_BPS() == PAY_ETH_BPS
    assert auto.r.getAUTOAddr() == auto.AUTO
    assert auto.r.getStakeManager() == auto.sm
    assert auto.r.getOracle() == auto.o
    assert auto.r.getUserForwarder() == auto.uf
    assert auto.r.getGasForwarder() == auto.ff
    assert auto.r.getUserGasForwarder() == auto.uff

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)
    
    assert auto.r.getHashedReqsUnveri() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, 1)
    assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
    assert auto.r.getHashedReqsUnveriLen() == 0
    with reverts():
        auto.r.getHashedReqUnveri(0)
    