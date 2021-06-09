from consts import *
from utils import *
from brownie import web3, chain


def test_getEpoch(auto):
    chain.mine(BLOCKS_IN_EPOCH - (bn() % BLOCKS_IN_EPOCH))
    assert bn() % BLOCKS_IN_EPOCH == 0
    startBlockNum = bn()

    for i in range(10):
        for j in range(BLOCKS_IN_EPOCH):
            assert auto.sm.getCurEpoch() == startBlockNum + (i * BLOCKS_IN_EPOCH)
            chain.mine(1)
