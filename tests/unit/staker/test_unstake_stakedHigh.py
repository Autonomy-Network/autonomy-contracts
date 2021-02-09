from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


def unstakeTest(
    asc,
    web3,
    numStakes,
    staker,
    curExec,
    maxNumStakes,
    startTotalNumStakes,
    startStakes
):
    assert asc.sm.getTotalStaked() == startTotalNumStakes * STAN_STAKE
    assert asc.sm.getStake(staker) == maxNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == startStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    assert asc.sm.getExecutor() == getExecutor(asc, web3.eth.blockNumber, startStakes) 
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == curExec)
    
    idxs, newStakes = getModStakes(startStakes, staker, 2, False)
    
    if len(idxs) == 0:
        with reverts(REV_MSG_NZ_UINT):
            asc.sm.unstake(idxs, {'from': staker})
    elif len(idxs) < maxNumStakes:
        tx = asc.sm.unstake(idxs, {'from': staker})

        assert asc.sm.getTotalStaked() == (startTotalNumStakes - len(idxs)) * STAN_STAKE
        assert asc.sm.getStake(staker) == (maxNumStakes - len(idxs)) * STAN_STAKE
        assert asc.sm.getStakes() == newStakes
        assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
        newExec, epoch = getExecutor(asc, web3.eth.blockNumber, startStakes)
        assert asc.sm.getExecutor() == (newExec, epoch)
        for addr in a:
            assert asc.sm.isCurExec(addr) == (addr == newExec)
        assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]
    else:
        with reverts(REV_MSG_EXCEED_BAL):
            asc.sm.unstake(idxs, {'from': staker})


@given(numStakes=strategy('uint256', max_value=INIT_NUM_STAKES))
def test_unstake(asc, stakedHigh, numStakes):
    startNumStakes, staker, __ = stakedHigh
    unstakeTest(
        asc,
        web3,
        numStakes,
        staker,
        staker,
        startNumStakes,
        startNumStakes,
        [staker] * startNumStakes
    )


# Want to have a few tests with specific, manual values because it's
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
    assert asc.sm.getStakes() == [staker] * curNumStakes
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