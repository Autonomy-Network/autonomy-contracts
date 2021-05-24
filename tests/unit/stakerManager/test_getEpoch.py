from consts import *
from utils import *
from brownie import web3, chain


def test_getEpoch(asc):
    chain.mine(BLOCKS_IN_EPOCH - (web3.eth.block_number % BLOCKS_IN_EPOCH))
    assert web3.eth.block_number % BLOCKS_IN_EPOCH == 0
    startBlockNum = web3.eth.block_number

    for i in range(10):
        for j in range(BLOCKS_IN_EPOCH):
            assert asc.sm.getCurEpoch() == startBlockNum + (i * BLOCKS_IN_EPOCH)
            chain.mine(1)
