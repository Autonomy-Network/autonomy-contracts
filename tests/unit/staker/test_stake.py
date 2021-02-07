from consts import *
from brownie import chain, reverts, web3
from utils import *
from brownie.test import given, strategy


# Can't do this as a module because the amount staked needs to vary
def setupStake(asc, num):
    staker = asc.BOB
    tx = asc.sm.stake(num, {'from': staker})
    return num, staker, tx


def stakeTest(asc, num, staker, tx):
    amount = num * STAN_STAKE
    # Brownie/Ganache still retains the increase in block height from other tests,
    # even though they've been reverted, which adversely affects this test by changing
    # the epoch, so we have to call updateExecutor
    asc.sm.updateExecutor()
    assert asc.sm.getStakes() == [staker] * num
    assert asc.sm.getStake(staker) == amount
    assert asc.sm.getStakeIdxs(staker) == [i for i in range(num)]
    assert asc.sm.getTotalStaked() == amount
    assert asc.sm.isCurExec(staker) == True
    assert tx.events["Staked"][0].values() == [staker, amount]


@given(num=strategy('uint256', min_value=1, max_value=INIT_NUM_STAKES, exclude=0))
def test_stake(asc, num):
    stakeTest(asc, *setupStake(asc, num))


# For some reason having test_stake_high after test_stake_min makes
# the former fail, not sure why, seems like a bug in the way Brownie reverts after?
def test_stake_high(a, asc):
    stakeTest(asc, *setupStake(asc, INIT_NUM_STAKES))


def test_stake_min(asc, stakedMin):
    stakeTest(asc, *stakedMin)


# Should probably be an integration test instead
def test_stake_multi(asc, stakedMulti, web3):
    nums, stakers, txs = stakedMulti
    stakes = []
    cumNumStanStakes = 0
    stakerToNum = {}
    stakerToIdxs = {}
    
    for (n, s, tx) in zip(nums, stakers, txs):
        stakes += [s] * n

        if s in stakerToNum:
            stakerToNum[s] += n
        else:
            stakerToNum[s] = n
        
        idxs = [i for i in range(cumNumStanStakes, cumNumStanStakes + n)]
        if s in stakerToIdxs:
            stakerToIdxs[s] += idxs
        else:
            stakerToIdxs[s] = idxs
        
        cumNumStanStakes += n
        assert tx.events["Staked"][0].values() == [s, n * STAN_STAKE]
    
    for s in stakerToNum:
        assert asc.sm.getStake(s) == stakerToNum[s] * STAN_STAKE
        assert asc.sm.getStakeIdxs(s) == stakerToIdxs[s]
        exec, epoch = getExecutor(web3.eth.blockNumber, stakes)
        isExec = exec == s
        assert asc.sm.isCurExec(s) == isExec

    assert asc.sm.getTotalStaked() == cumNumStanStakes * STAN_STAKE
    assert asc.sm.getStakes() == stakes
    assert asc.sm.getExecutor() == (exec, epoch)


def test_stake_rev_numStanStakes(asc):
    with reverts(REV_MSG_NZ_UINT):
        asc.sm.stake(0, {'from': asc.ALICE})


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_stake_rev_noFish(asc, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    vStaker.vulnerableTransfer(asc.DENICE, amount)

    with reverts(REV_MSG_NOFISH):
        vStaker.stake(1, {'from': staker})