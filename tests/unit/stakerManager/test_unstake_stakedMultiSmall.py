from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Want to have a few tests with specific, manual values because it's
# possible that some of the slightly more complex algorithms in StakeManager have
# errors and I've just replicated those errors in things like getModStakes()


# Unstake 3 from the 4th staker in stakedMultiSmall
# For some reason, having this test below the others in this file causes some to fail
def test_unstake_3_of_4th_staker_from_stakedMultiSmall(auto, evmMaths, stakedMultiSmall):
    nums, stakers, startStakes, _ = stakedMultiSmall
    assert len(startStakes) == 7
    assert auto.sm.getStakes() == [auto.ALICE, auto.BOB, auto.BOB, auto.CHARLIE, auto.CHARLIE, auto.BOB, auto.BOB]
    assert auto.sm.getStakes() == startStakes
    assert auto.sm.getStakesLength() == len(startStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(startStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(startStakes)) == startStakes
    staker = stakers[3]
    assert staker == auto.BOB
    idxs = [1, 1, 1]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 3, False)
    assert idxs == calcIdxs
    
    tx = auto.sm.unstake(idxs, {'from': staker})

    curNumStakes = 1
    assert auto.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert auto.sm.getStake(staker) == curNumStakes * STAN_STAKE
    assert auto.sm.getStakes() == [auto.ALICE, auto.CHARLIE, auto.BOB, auto.CHARLIE]
    assert auto.sm.getStakes() == newStakes
    assert auto.sm.getStakesLength() == len(newStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(newStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(newStakes)) == newStakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    newExec, epoch = getExecutor(evmMaths, bn(), startStakes, None)
    assert auto.sm.getExecutor() == (newExec, epoch)
    if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
        assert auto.sm.isUpdatedExec(newExec).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


# Unstake 1 from the 2nd staker in stakedMultiSmall
def test_unstake_1_of_2nd_staker_from_stakedMultiSmall(auto, evmMaths, stakedMultiSmall):
    nums, stakers, startStakes, _ = stakedMultiSmall
    assert len(startStakes) == 7
    assert auto.sm.getStakes() == startStakes
    assert auto.sm.getStakes() == [auto.ALICE, auto.BOB, auto.BOB, auto.CHARLIE, auto.CHARLIE, auto.BOB, auto.BOB]
    assert auto.sm.getStakesLength() == len(startStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(startStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(startStakes)) == startStakes
    staker  = stakers[1]
    idxs = [1]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 1, False)
    assert idxs == calcIdxs

    tx = auto.sm.unstake(idxs, {'from': staker})

    curNumStakes = 3
    assert auto.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert auto.sm.getStake(staker) == curNumStakes * STAN_STAKE
    assert auto.sm.getStakes() == [auto.ALICE, auto.BOB, auto.BOB, auto.CHARLIE, auto.CHARLIE, auto.BOB]
    assert auto.sm.getStakes() == newStakes
    assert auto.sm.getStakesLength() == len(newStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(newStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(newStakes)) == newStakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    newExec, epoch = getExecutor(evmMaths, bn(), startStakes, None)
    assert auto.sm.getExecutor() == (newExec, epoch)
    if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
        assert auto.sm.isUpdatedExec(newExec).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


# Unstake 2 from the 3rd staker in stakedMultiSmall
def test_unstake_2_of_3rd_staker_from_stakedMultiSmall(auto, evmMaths, stakedMultiSmall):
    nums, stakers, startStakes, _ = stakedMultiSmall
    assert len(startStakes) == 7
    assert auto.sm.getStakes() == [auto.ALICE, auto.BOB, auto.BOB, auto.CHARLIE, auto.CHARLIE, auto.BOB, auto.BOB]
    assert auto.sm.getStakes() == startStakes
    assert auto.sm.getStakesLength() == len(startStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(startStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(startStakes)) == startStakes
    staker = stakers[2]
    idxs = [3, 4]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 2, False)
    assert auto.sm.getStakes() == startStakes
    assert idxs == calcIdxs

    tx = auto.sm.unstake(idxs, {'from': staker})

    curNumStakes = 0
    assert auto.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert auto.sm.getStake(staker) == 0
    assert auto.sm.getStakes() == [auto.ALICE, auto.BOB, auto.BOB, auto.BOB, auto.BOB]
    assert auto.sm.getStakes() == newStakes
    assert auto.sm.getStakesLength() == len(newStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(newStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(newStakes)) == newStakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    newExec, epoch = getExecutor(evmMaths, bn(), startStakes, None)
    assert auto.sm.getExecutor() == (newExec, epoch)
    if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
        assert auto.sm.isUpdatedExec(newExec).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


# Using an index that isn't the caller
def test_unstake_rev_wrong_idx(auto, stakedMultiSmall):
    with reverts(REV_MSG_NOT_STAKER):
        auto.sm.unstake([0], auto.FR_BOB)


# Using indexes that are correct initially but don't account for how
# staker changes as the end of the array is moved to a just-deleted element
def test_unstake_rev_wrong_idxs_from_shift(auto, stakedMultiSmall):
    with reverts():
        auto.sm.unstake([1, 2, 5, 6], auto.FR_BOB)


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_unstake_rev_noFish(auto, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    auto.AUTO.authorizeOperator(vStaker, {'from': staker})
    vStaker.vulnerableTransfer(auto.DENICE, amount)

    with reverts(REV_MSG_NOFISH):
        vStaker.unstake([0], {'from': staker})