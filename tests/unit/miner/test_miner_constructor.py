from consts import *


def test_constructor(a, auto):
    assert auto.m.getAUTOPerReq() == INIT_REQUESTER_REWARD
    assert auto.m.getAUTOPerExec() == INIT_EXECUTOR_REWARD
    assert auto.m.getAUTOPerReferal() == INIT_REFERAL_REWARD
    assert auto.AUTO.balanceOf(auto.m) == INIT_AUTO_REW_POOL

    for addr in a:
        assert auto.m.getMinedReqCountOf(addr) == 0
        assert auto.m.getMinedExecCountOf(addr) == 0
        assert auto.m.getMinedReferalCountOf(addr) == 0
        assert auto.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)