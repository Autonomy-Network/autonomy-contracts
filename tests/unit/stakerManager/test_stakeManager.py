from consts import *
from utils import *


def test_constructor(asc, web3):
    assert asc.sm.getOracle() == asc.o.address
    assert asc.sm.getASCoin() == asc.ASC.address
    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getStake(asc.DEPLOYER) == 0
    assert len(asc.sm.getStakes()) == 0
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.block_number)