from consts import *
from brownie import chain, reverts, web3
from utils import *
from brownie.test import given, strategy


# Can't do this as a module because the amount staked needs to vary
def setupStake(auto, num):
    staker = auto.BOB
    tx = auto.sm.stake(num, {'from': staker})

    return num, staker, tx


def stakeTest(auto, num, staker, tx):
    amount = num * STAN_STAKE
    # Brownie/Ganache still retains the increase in block height from other tests,
    # even though they've been reverted, which adversely affects this test by changing
    # the epoch, so we have to call updateExecutor
    assert auto.sm.isUpdatedExec(staker).return_value
    stakes = [staker] * num
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getStakesLength() == num
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, num + 1)
    assert auto.sm.getStakesSlice(0, num) == stakes
    assert auto.sm.getStake(staker) == amount
    assert auto.sm.getTotalStaked() == amount
    assert auto.sm.isCurExec(staker)
    assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
    assert tx.events["Staked"][0].values() == [staker, amount]


@given(num=strategy('uint256', min_value=1, max_value=INIT_NUM_STAKES, exclude=0))
def test_stake(auto, num):
    stakeTest(auto, *setupStake(auto, num))


def test_stake_high(a, auto):
    stakeTest(auto, *setupStake(auto, INIT_NUM_STAKES))


def test_stake_min(auto, stakedMin):
    stakeTest(auto, *stakedMin)


# The 1st stake/unstake of an epoch should change the executor before the stake change, otherwise
# a staker could precalculate the effect of how much they stake in order to
# game the staker selection algo
def test_stake_1st_stake_of_epoch_no_exec_change(auto, stakedMin):
    numStakes, staker, oldTx = stakedMin
    blockNum = bn()
    
    # Can't know what the current numerical value of the block number is so
    # mine until xx99 such that the next tx is in the new epoch
    chain.mine(BLOCKS_IN_EPOCH - (blockNum % BLOCKS_IN_EPOCH) - 1)
    assert bn() % BLOCKS_IN_EPOCH == BLOCKS_IN_EPOCH - 1

    # Stake a different staker with a large amount such that it's very likely
    # they would be the new executor if it was a new epoch after their stake
    # had taken effect
    newStaker = auto.CHARLIE
    newNumStakes = INIT_NUM_STAKES
    tx = auto.sm.stake(newNumStakes, {'from': newStaker})

    stakes = [staker] + ([newStaker] * newNumStakes)
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(stakes) + 1)
    assert auto.sm.getStakesSlice(0, len(stakes)) == stakes
    assert auto.sm.getStake(newStaker) == newNumStakes * STAN_STAKE
    assert auto.sm.getTotalStaked() == (numStakes + newNumStakes) * STAN_STAKE
    # Old staker but new epoch
    assert auto.sm.getExecutor() == (staker, getEpoch(bn()))
    assert auto.sm.isCurExec(staker)
    assert auto.sm.isUpdatedExec(staker).return_value
    assert tx.events["Staked"][0].values() == [newStaker, newNumStakes * STAN_STAKE]


def test_stake_rev_numStanStakes(auto):
    with reverts(REV_MSG_NZ_UINT):
        auto.sm.stake(0, {'from': auto.ALICE})


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_stake_rev_noFish(auto, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    auto.AUTO.authorizeOperator(vStaker, {'from': staker})
    vStaker.vulnerableTransfer(auto.DENICE, amount)

    with reverts(REV_MSG_NOFISH):
        vStaker.stake(1, {'from': staker})