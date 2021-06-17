from consts import *
from brownie import chain, reverts, web3
from utils import *
from brownie.test import given, strategy


def test_stake_multi(auto, evmMaths, stakedMulti):
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
    
    exec, epoch = getExecutor(evmMaths, bn() + 1, stakes, None)
    assert auto.sm.isUpdatedExec(exec).return_value
    for s in stakerToNum:
        assert auto.sm.getStake(s) == stakerToNum[s] * STAN_STAKE
        isExec = exec == s
        assert auto.sm.isCurExec(s) == isExec

    assert auto.sm.getTotalStaked() == cumNumStanStakes * STAN_STAKE
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        auto.sm.getStakesSlice(0, len(stakes) + 1)
    assert auto.sm.getStakesSlice(0, len(stakes)) == stakes
    assert auto.sm.getExecutor() == (exec, epoch)