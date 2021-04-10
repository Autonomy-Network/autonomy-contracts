from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def unstakeTest(
    asc,
    web3,
    numUnstakes,
    staker,
    curExec,
    maxNumStakes,
    startTotalNumStakes,
    startStakes
):
    assert asc.sm.getTotalStaked() == startTotalNumStakes * STAN_STAKE
    assert asc.sm.getStake(staker) == maxNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == startStakes
    assert asc.sm.getStakesLength() == len(startStakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        asc.sm.getStakesSlice(0, len(startStakes) + 1)
    assert asc.sm.getStakesSlice(0, len(startStakes)) == startStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    assert asc.sm.getExecutor() == getExecutor(asc, web3.eth.blockNumber, startStakes) 
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == curExec)
    
    if numUnstakes == 0:
        with reverts(REV_MSG_NZ_UINT_ARR):
            asc.sm.unstake([], {'from': staker})
    elif numUnstakes > maxNumStakes:
        with reverts(REV_MSG_NOT_ENOUGH_STAKE):
            asc.sm.unstake([i for i in range(maxNumStakes+1)], {'from': staker})
    else:
        idxs, newStakes = getModStakes(startStakes, staker, numUnstakes, False)

        tx = asc.sm.unstake(idxs, {'from': staker})

        assert asc.sm.getTotalStaked() == (startTotalNumStakes - len(idxs)) * STAN_STAKE
        assert asc.sm.getStake(staker) == (maxNumStakes - len(idxs)) * STAN_STAKE
        assert asc.sm.getStakes() == newStakes
        assert asc.sm.getStakesLength() == len(newStakes)
        # Should revert if requesting an index that is above the max
        with reverts():
            asc.sm.getStakesSlice(0, len(newStakes) + 1)
        assert asc.sm.getStakesSlice(0, len(newStakes)) == newStakes
        assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
        newExec, epoch = getExecutor(asc, web3.eth.blockNumber, startStakes)
        assert asc.sm.getExecutor() == (newExec, epoch)
        for addr in a:
            # If all stakes are unstaked, it'll return true for any address
            assert asc.sm.isCurExec(addr) == ((addr == newExec) if len(idxs) != maxNumStakes else True)
        assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


@given(numUnstakes=strategy('uint256', max_value=INIT_NUM_STAKES + 20))
def test_unstake(asc, stakedHigh, numUnstakes):
    startNumStakes, staker, __ = stakedHigh
    unstakeTest(
        asc,
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
def test_unstake_7(asc, stakedHigh):
    chain.mine(BLOCKS_IN_EPOCH)
    startNumStakes, staker, = 100, asc.ALICE
    idxs = [0, 0, 0, 0, 0, 0, 0]
    tx = asc.sm.unstake(idxs, {'from': staker})

    curNumStakes = startNumStakes - len(idxs)
    assert asc.sm.getTotalStaked() == curNumStakes * STAN_STAKE
    assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
    stakes = [staker] * curNumStakes
    assert asc.sm.getStakes() == stakes
    assert asc.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        asc.sm.getStakesSlice(0, len(stakes) + 1)
    assert asc.sm.getStakesSlice(0, len(stakes)) == stakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(asc, web3.eth.blockNumber, [staker] * startNumStakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


def test_unstake_rev_idxs(asc, stakedHigh):
    with reverts(REV_MSG_NZ_UINT_ARR):
        asc.sm.unstake([], asc.FR_ALICE)


def test_unstake_rev_too_much_stake(asc, stakedHigh):
    with reverts(REV_MSG_NOT_ENOUGH_STAKE):
        asc.sm.unstake([0], asc.FR_BOB)