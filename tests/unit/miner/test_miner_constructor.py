from consts import *


def test_constructor(a, asc):
    assert asc.m.getASCPerReq() == INIT_REQUESTER_REWARD
    assert asc.m.getASCPerExec() == INIT_EXECUTOR_REWARD
    assert asc.m.getASCPerReferal() == INIT_REFERAL_REWARD
    assert asc.ASC.balanceOf(asc.m) == INIT_ASC_REW_POOL

    for addr in a:
        assert asc.m.getMinedReqCountOf(addr) == 0
        assert asc.m.getMinedExecCountOf(addr) == 0
        assert asc.m.getMinedReferalCountOf(addr) == 0
        assert asc.m.getAvailableMiningRewards(addr) == (0, 0, 0, 0)