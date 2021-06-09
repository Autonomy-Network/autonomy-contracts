from consts import *
from utils import *
from brownie import web3, chain
from brownie import reverts


# When there are no current stakers, should return true for any address
def test_isCurExec_no_stakes(a, auto):
    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getStakesLength() == 0
    with reverts():
        auto.sm.getStakesSlice(0, 1)
    assert auto.sm.getStakesSlice(0, 0) == []
    assert auto.sm.getExecutor() == NULL_EXEC

    for addr in a:
        assert auto.sm.isUpdatedExec(addr).return_value
        assert auto.sm.isCurExec(addr)
    
    chain.mine(BLOCKS_IN_EPOCH)

    for addr in a:
        assert auto.sm.isCurExec(addr)


def test_isCurExec(a, auto, stakedMin):
    numStanStakes, exec, tx = stakedMin
    assert auto.sm.getTotalStaked() == numStanStakes * STAN_STAKE
    assert auto.sm.getStakesLength() == numStanStakes
    assert auto.sm.getStakesSlice(0, numStanStakes) == [exec] * numStanStakes
    assert auto.sm.getExecutor() == (exec, getEpoch(bn()))

    # Should only be true when the input is the executor
    for addr in a:
        assert auto.sm.isUpdatedExec(addr).return_value == (addr == exec)
        assert auto.sm.isCurExec(addr) == (addr == exec)
    
    chain.mine(BLOCKS_IN_EPOCH)

    # Should always be false in another epoch when the executor hasn't been updated
    for addr in a:
        assert not auto.sm.isCurExec(addr)


# Should return true for every address after enough unstakes leave no stakes left
# in future epochs
def test_isCurExec_after_all_unstaked(a, auto, stakedMin):
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