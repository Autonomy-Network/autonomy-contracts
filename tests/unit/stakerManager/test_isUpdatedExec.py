from consts import *
from utils import *
from brownie import web3, chain
from brownie import reverts
from random import choice


# When there are no current stakers, should return true for any address
def test_isUpdatedExec_no_stakes(a, auto):
    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getStakesLength() == 0
    with reverts():
        auto.sm.getStakesSlice(0, 1)
    assert auto.sm.getStakesSlice(0, 0) == []
    assert auto.sm.getExecutor() == NULL_EXEC

    for addr in a:
        assert auto.sm.isUpdatedExec(addr).return_value
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert auto.sm.isUpdatedExec(addr).return_value


# Since isUpdatedExec is an actual transaction, we can't test every address
# as input for a given block height, so we'll have this test to test inputing
# the executor returns true for every block that it should, and 
# test_isUpdatedExec_false for testing inputs that aren't the executor fail
def test_isUpdatedExec_true(a, auto, evmMaths, stakedMin):
    numStanStakes, exec, tx = stakedMin
    auto.sm.stake(1, auto.FR_BOB)
    auto.sm.stake(1, auto.FR_CHARLIE)
    totalNumStakes = numStanStakes + 2
    stakes = ([exec] * numStanStakes) + [auto.BOB, auto.CHARLIE]
    assert auto.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert auto.sm.getStakesLength() == totalNumStakes
    assert auto.sm.getStakesSlice(0, totalNumStakes) == stakes
    assert auto.sm.getExecutor() == (exec, getEpoch(bn()))

    chain.mine(BLOCKS_IN_EPOCH)

    for i in range(5 * BLOCKS_IN_EPOCH):
        exec, epoch = getExecutor(evmMaths, bn() + 1, stakes, None)
        assert auto.sm.isUpdatedExec(exec).return_value
        assert auto.sm.isCurExec(exec)


def test_isUpdatedExec_false(a, auto, evmMaths, stakedMin):
    a = list(a)
    numStanStakes, exec, tx = stakedMin
    auto.sm.stake(1, auto.FR_BOB)
    auto.sm.stake(1, auto.FR_CHARLIE)
    totalNumStakes = numStanStakes + 2
    stakes = ([exec] * numStanStakes) + [auto.BOB, auto.CHARLIE]
    assert auto.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert auto.sm.getStakesLength() == totalNumStakes
    assert auto.sm.getStakesSlice(0, totalNumStakes) == stakes
    assert auto.sm.getExecutor() == (exec, getEpoch(bn()))

    chain.mine(BLOCKS_IN_EPOCH)

    for i in range(5 * BLOCKS_IN_EPOCH):
        exec, epoch = getExecutor(evmMaths, bn() + 1, stakes, None)
        addr = choice(a)
        if addr != exec:
            assert not auto.sm.isUpdatedExec(addr).return_value
            assert not auto.sm.isCurExec(addr)


# Should return true for every address after enough unstakes leave no stakes left
# in future epochs
def test_isUpdatedExec_after_all_unstaked(a, auto, stakedMin):
    numStanStakes, exec, tx = stakedMin

    auto.sm.unstake([0], auto.FR_ALICE)

    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getStakesLength() == 0
    with reverts():
        auto.sm.getStakesSlice(0, 1)
    assert auto.sm.getStakesSlice(0, 0) == []
    assert auto.sm.getExecutor() == (exec, getEpoch(bn()))

    assert auto.sm.isUpdatedExec(exec).return_value
    assert auto.sm.isCurExec(exec)
    for addr in a:
        if addr != exec:
            assert not auto.sm.isUpdatedExec(addr).return_value
            assert not auto.sm.isCurExec(addr)
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert auto.sm.isUpdatedExec(addr).return_value
        assert auto.sm.isCurExec(addr)