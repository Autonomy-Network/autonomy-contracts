from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# updateExecutor should do nothing if there's nothing staked
def test_updateExecutor_no_stake_do_nothing(a, auto):
    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getExecutor() == NULL_EXEC
    for addr in a:
        assert auto.sm.isCurExec(addr)

    tx = auto.sm.updateExecutor(auto.FR_ALICE)

    assert tx.return_value == (getEpoch(bn()), 0, 0, ADDR_0)
    assert auto.sm.getExecutor() == NULL_EXEC
    for addr in a:
        assert auto.sm.isCurExec(addr)
    assert auto.sm.isUpdatedExec(addr).return_value


def test_updateExecutor_stakedMin(auto, evmMaths, stakedMin):
    numStanStakes, staker, tx = stakedMin
    assert auto.sm.getTotalStaked() == numStanStakes * STAN_STAKE
    assert auto.sm.getExecutor() == getExecutor(evmMaths, bn(), [staker], None)
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == staker)


# updateExecutor should do nothing if the epoch hasn't changed
def test_updateExecutor_same_epoch(a, auto, evmMaths, stakedMin):
    numStanStakes, staker, tx = stakedMin
    # Make sure we're on block number xxx99 so that updateExecutor will be called
    # at the start of the next epoch and we can test every single block in the epoch
    chain.mine(BLOCKS_IN_EPOCH - (bn() % BLOCKS_IN_EPOCH) - 1)
    assert bn() % BLOCKS_IN_EPOCH == BLOCKS_IN_EPOCH - 1

    # Ensure the current executor is set at the start of the epoch
    tx = auto.sm.updateExecutor(auto.FR_ALICE)

    assert bn() % BLOCKS_IN_EPOCH == 0
    assert tx.return_value == getUpdatedExecResult(evmMaths, bn(), [staker], 0)
    assert auto.sm.isUpdatedExec(staker).return_value
    assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == staker)
    
    # Make Bob the only one with stake in the contract to ensure that if updateExecutor
    # is called such that it changed executor, it would change to Bob
    auto.sm.unstake([i for i in range(numStanStakes)], auto.FR_ALICE)
    
    # Alice is still the exec until the next epoch tho
    staker2 = auto.BOB
    assert auto.sm.isUpdatedExec(staker).return_value
    assert not auto.sm.isUpdatedExec(staker2).return_value
    assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
    assert auto.sm.isCurExec(staker)
    for addr in a:
        if addr != staker:
            assert not auto.sm.isCurExec(addr)
    
    auto.sm.stake(INIT_NUM_STAKES, auto.FR_BOB)

    assert auto.sm.isUpdatedExec(staker).return_value
    assert not auto.sm.isUpdatedExec(staker2).return_value
    assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
    assert auto.sm.isCurExec(staker)
    for addr in a:
        if addr != staker:
            assert not auto.sm.isCurExec(addr)

    stakes = [staker2] * INIT_NUM_STAKES
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(stakes) + 1)
    assert auto.sm.getStakesSlice(0, len(stakes)) == stakes

    # Make sure that updateExecutor doesn't change the executor for every remaining block in the epoch
    while bn() % BLOCKS_IN_EPOCH != 99:
        assert auto.sm.updateExecutor(auto.FR_ALICE).return_value == (getEpoch(bn()), 0, 0, ADDR_0)
        assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
        assert auto.sm.isCurExec(staker)
        for addr in a:
            assert auto.sm.isCurExec(addr) == (addr == staker)
    
    # Check that it does change the executor to Bob in the next block
    assert bn() % BLOCKS_IN_EPOCH == 99
    
    tx = auto.sm.updateExecutor(auto.FR_ALICE)
    
    assert tx.return_value == getUpdatedExecResult(evmMaths, bn(), stakes, getEpoch(bn())-BLOCKS_IN_EPOCH)
    assert bn() % BLOCKS_IN_EPOCH == 0
    assert auto.sm.getExecutor() == (staker2, getEpoch(bn()))
    assert not auto.sm.isUpdatedExec(staker).return_value
    assert auto.sm.isUpdatedExec(staker2).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == staker2)


def test_updateExecutor_stakedMulti(auto, evmMaths, stakedMulti):
    stakes = auto.sm.getStakes()
    for i in range(BLOCKS_IN_EPOCH * 2):
        tx = auto.sm.updateExecutor(auto.FR_ALICE)

        exec, epoch = getExecutor(evmMaths, bn(), stakes, None)
        assert auto.sm.getExecutor() == (exec, epoch)
        if bn() % BLOCKS_IN_EPOCH == 0:
            assert tx.return_value == getUpdatedExecResult(evmMaths, bn(), stakes, epoch - BLOCKS_IN_EPOCH)
        else:
            assert tx.return_value == (epoch, 0, 0, ADDR_0)
        for addr in a:
            assert auto.sm.isCurExec(addr) == (addr == exec)


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_updateExecutor_rev_noFish_same_epoch(auto, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    vStaker.updateExecutor(auto.FR_ALICE)
    vStaker.vulnerableTransfer(auto.DENICE, amount)

    with reverts(REV_MSG_NOFISH):
        vStaker.updateExecutor(auto.FR_ALICE)


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_updateExecutor_rev_noFish_different_epoch(auto, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    vStaker.updateExecutor(auto.FR_ALICE)
    vStaker.vulnerableTransfer(auto.DENICE, amount)
    chain.mine(BLOCKS_IN_EPOCH)

    with reverts(REV_MSG_NOFISH):
        vStaker.updateExecutor(auto.FR_ALICE)