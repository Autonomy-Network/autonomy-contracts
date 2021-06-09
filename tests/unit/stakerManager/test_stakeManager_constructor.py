from consts import *
from utils import *


def test_constructor(auto, web3):
    assert auto.sm.getOracle() == auto.o.address
    assert auto.sm.getAUTO() == auto.AUTO.address
    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getStake(auto.DEPLOYER) == 0
    assert len(auto.sm.getStakes()) == 0
    assert auto.sm.getCurEpoch() == getEpoch(bn())