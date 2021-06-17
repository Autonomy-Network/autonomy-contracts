from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def unstakeTest(
    auto,
    evmMaths,
    web3,
    numUnstakes,
    staker,
    curExec,
    maxNumStakes,
    startTotalNumStakes,
    startStakes
):
    assert auto.sm.getTotalStaked() == startTotalNumStakes * STAN_STAKE
    assert auto.sm.getStake(staker) == maxNumStakes * STAN_STAKE
    assert auto.sm.getStakes() == startStakes
    assert auto.sm.getStakesLength() == len(startStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(startStakes) + 1)
    assert auto.sm.getStakesSlice(0, len(startStakes)) == startStakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    prevExec = getExecutor(evmMaths, bn(), startStakes, None)
    assert auto.sm.getExecutor() == prevExec
    if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
        assert auto.sm.isUpdatedExec(staker).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == curExec)
    
    if numUnstakes == 0:
        with reverts(REV_MSG_NZ_UINT_ARR):
            auto.sm.unstake([], {'from': staker})
    elif numUnstakes > maxNumStakes:
        with reverts(REV_MSG_NOT_ENOUGH_STAKE):
            auto.sm.unstake([i for i in range(maxNumStakes+1)], {'from': staker})
    else:
        idxs, newStakes = getModStakes(startStakes, staker, numUnstakes, False)

        tx = auto.sm.unstake(idxs, {'from': staker})

        assert auto.sm.getTotalStaked() == (startTotalNumStakes - len(idxs)) * STAN_STAKE
        assert auto.sm.getStake(staker) == (maxNumStakes - len(idxs)) * STAN_STAKE
        assert auto.sm.getStakes() == newStakes
        assert auto.sm.getStakesLength() == len(newStakes)
        # Should revert if requesting an index that is above the max
        with reverts():
            auto.sm.getStakesSlice(0, len(newStakes) + 1)
        assert auto.sm.getStakesSlice(0, len(newStakes)) == newStakes
        assert auto.sm.getCurEpoch() == getEpoch(bn())
        newExec, epoch = getExecutor(evmMaths, bn(), startStakes, prevExec)
        assert auto.sm.getExecutor() == (newExec, epoch)
        if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
            assert auto.sm.isUpdatedExec(newExec).return_value
        for addr in a:
            # If all stakes are unstaked, it'll return true for any address
            assert auto.sm.isCurExec(addr) == (addr == curExec)
        assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


@given(numUnstakes=strategy('uint256', max_value=INIT_NUM_STAKES + 20))
def test_unstake(auto, evmMaths, stakedHigh, numUnstakes):
    startNumStakes, staker, __ = stakedHigh
    unstakeTest(
        auto,
        evmMaths,
        web3,
        numUnstakes,
        staker,
        staker,
        startNumStakes,
        startNumStakes,
        [staker] * startNumStakes
    )


# Want to have some tests with specific, manual values because it's
# possible that some of the slightly more complex algorithms in StakeManager have
# errors and I've just replicated those errors in things like getModStakes()
def test_unstake_7(auto, evmMaths, stakedHigh):
    chain.mine(BLOCKS_IN_EPOCH)
    startNumStakes, staker, = 100, auto.ALICE
    idxs = [0, 0, 0, 0, 0, 0, 0]
    tx = auto.sm.unstake(idxs, {'from': staker})

    curNumStakes = startNumStakes - len(idxs)
    assert auto.sm.getTotalStaked() == curNumStakes * STAN_STAKE
    assert auto.sm.getStake(staker) == curNumStakes * STAN_STAKE
    stakes = [staker] * curNumStakes
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(stakes) + 1)
    assert auto.sm.getStakesSlice(0, len(stakes)) == stakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    newExec, epoch = getExecutor(evmMaths, bn(), [staker] * startNumStakes, None)
    assert auto.sm.getExecutor() == (newExec, epoch)
    if bn() % BLOCKS_IN_EPOCH != BLOCKS_IN_EPOCH - 1:
        assert auto.sm.isUpdatedExec(newExec).return_value
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


def test_unstake_rev_idxs(auto, stakedHigh):
    with reverts(REV_MSG_NZ_UINT_ARR):
        auto.sm.unstake([], auto.FR_ALICE)


def test_unstake_rev_too_much_stake(auto, stakedHigh):
    with reverts(REV_MSG_NOT_ENOUGH_STAKE):
        auto.sm.unstake([0], auto.FR_BOB)