from consts import *
from utils import *
from brownie import web3, chain
from brownie import reverts
from brownie.test import given, strategy


# When there are no current stakers, should return true for any address
def test_isCurExec_no_stakes(a, asc):
    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getStakesLength() == 0
    with reverts():
        asc.sm.getStakesSlice(0, 1)
    assert asc.sm.getStakesSlice(0, 0) == []
    assert asc.sm.getExecutor() == NULL_EXEC

    for addr in a:
        assert asc.sm.isCurExec(addr) == True
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert asc.sm.isCurExec(addr) == True


def test_isCurExec(a, asc, stakedMin):
    numStanStakes, exec, tx = stakedMin
    assert asc.sm.getTotalStaked() == numStanStakes * STAN_STAKE
    assert asc.sm.getStakesLength() == numStanStakes
    assert asc.sm.getStakesSlice(0, numStanStakes) == [exec] * numStanStakes
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    # Should only be true when the input is the executor
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == exec)
    
    chain.mine(BLOCKS_IN_EPOCH)

    # Should always be false in another epoch when the executor hasn't been updated
    for addr in a:
        assert asc.sm.isCurExec(addr) == False


# Should return true for every address after enough unstakes leave no stakes left
# immediately and in future epochs
def test_isCurExec_after_all_unstaked(a, asc, stakedMin):
    numStanStakes, exec, tx = stakedMin

    asc.sm.unstake([0], asc.FR_ALICE)

    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getStakesLength() == 0
    with reverts():
        asc.sm.getStakesSlice(0, 1)
    assert asc.sm.getStakesSlice(0, 0) == []
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    for addr in a:
        assert asc.sm.isCurExec(addr) == True
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert asc.sm.isCurExec(addr) == True