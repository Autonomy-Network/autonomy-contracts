from consts import *
from utils import *
from brownie import web3, chain


def test_isCurExec(asc, stakedMin):
    numStanStakes, exec, tx = stakedMin
    assert asc.sm.getTotalStaked() == numStanStakes * STAN_STAKE
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    # Should only be true when the input is the executor and 
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == exec)
    
    chain.mine(BLOCKS_IN_EPOCH)

    # Should always be false in another epoch when the executor hasn't been updated
    for addr in a:
        assert asc.sm.isCurExec(addr) == False