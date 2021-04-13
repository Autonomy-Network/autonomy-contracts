from consts import *
from utils import *
from brownie import web3, chain
from brownie import reverts
from random import choice


# When there are no current stakers, should return true for any address
def test_isUpdatedExec_no_stakes(a, asc):
    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getStakesLength() == 0
    with reverts():
        asc.sm.getStakesSlice(0, 1)
    assert asc.sm.getStakesSlice(0, 0) == []
    assert asc.sm.getExecutor() == NULL_EXEC

    for addr in a:
        assert asc.sm.isUpdatedExec(addr).return_value
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert asc.sm.isUpdatedExec(addr).return_value


# Since isUpdatedExec is an actual transaction, we can't test every address
# as input for a given block height, so we'll have this test to test inputing
# the executor returns true for every block that it should, and 
# test_isUpdatedExec_false for testing inputs that aren't the executor fail
def test_isUpdatedExec_true(a, asc, stakedMin):
    numStanStakes, exec, tx = stakedMin
    asc.sm.stake(1, asc.FR_BOB)
    asc.sm.stake(1, asc.FR_CHARLIE)
    totalNumStakes = numStanStakes + 2
    stakes = ([exec] * numStanStakes) + [asc.BOB, asc.CHARLIE]
    assert asc.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert asc.sm.getStakesLength() == totalNumStakes
    assert asc.sm.getStakesSlice(0, totalNumStakes) == stakes
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    chain.mine(BLOCKS_IN_EPOCH)

    for i in range(5 * BLOCKS_IN_EPOCH):
        exec, epoch = getExecutor(asc, web3.eth.blockNumber + 1, stakes)
        assert asc.sm.isUpdatedExec(exec).return_value
        assert asc.sm.isCurExec(exec)


def test_isUpdatedExec_false(a, asc, stakedMin):
    a = list(a)
    numStanStakes, exec, tx = stakedMin
    asc.sm.stake(1, asc.FR_BOB)
    asc.sm.stake(1, asc.FR_CHARLIE)
    totalNumStakes = numStanStakes + 2
    stakes = ([exec] * numStanStakes) + [asc.BOB, asc.CHARLIE]
    assert asc.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert asc.sm.getStakesLength() == totalNumStakes
    assert asc.sm.getStakesSlice(0, totalNumStakes) == stakes
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    chain.mine(BLOCKS_IN_EPOCH)

    for i in range(5 * BLOCKS_IN_EPOCH):
        exec, epoch = getExecutor(asc, web3.eth.blockNumber + 1, stakes)
        addr = choice(a)
        if addr != exec:
            assert not asc.sm.isUpdatedExec(addr).return_value
            assert not asc.sm.isCurExec(addr)


# Should return true for every address after enough unstakes leave no stakes left
# immediately and in future epochs
def test_isUpdatedExec_after_all_unstaked(a, asc, stakedMin):
    numStanStakes, exec, tx = stakedMin

    asc.sm.unstake([0], asc.FR_ALICE)

    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getStakesLength() == 0
    with reverts():
        asc.sm.getStakesSlice(0, 1)
    assert asc.sm.getStakesSlice(0, 0) == []
    assert asc.sm.getExecutor() == (exec, getEpoch(web3.eth.blockNumber))

    for addr in a:
        assert asc.sm.isUpdatedExec(addr).return_value
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert asc.sm.isUpdatedExec(addr).return_value