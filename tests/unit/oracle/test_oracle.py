from consts import *
from brownie import web3, chain
from utils import *


def test_getRandNum(asc):
    for i in range(1000):
        chain.mine(1)
        localRandNum = getRandNum(i)
        # assert (localRandNum * (1 - ERROR_FACTOR)) <= asc.o.getRandNum(i) <= (localRandNum * ERROR_FACTOR)
        assert localRandNum == asc.o.getRandNum(i)

