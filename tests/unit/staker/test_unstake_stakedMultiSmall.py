from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# Want to have a few tests with specific, manual values because it's
# possible that some of the slightly more complex algorithms in StakeManager have
# errors and I've just replicated those errors in things like getModStakes()


# Unstake 3 from the 4th staker in stakedMultiSmall
# For some reason, having this test elow the others in this file causes some to fail
def test_unstake_3_of_4th_staker_from_stakedMultiSmall(asc, stakedMultiSmall):
    nums, stakers, startStakes = stakedMultiSmall
    assert len(startStakes) == 7
    assert asc.sm.getStakes() == [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB, asc.BOB]
    assert asc.sm.getStakes() == startStakes
    staker = stakers[3]
    assert staker == asc.BOB
    idxs = [1, 1, 1]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 3, False)
    assert idxs == calcIdxs
    
    tx = asc.sm.unstake(idxs, {'from': staker})

    curNumStakes = 1
    assert asc.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == [asc.ALICE, asc.CHARLIE, asc.BOB, asc.CHARLIE]
    assert asc.sm.getStakes() == newStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(asc, web3.eth.blockNumber, startStakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


# Unstake 1 from the 2nd staker in stakedMultiSmall
def test_unstake_1_of_2nd_staker_from_stakedMultiSmall(asc, stakedMultiSmall):
    nums, stakers, startStakes = stakedMultiSmall
    assert len(startStakes) == 7
    assert asc.sm.getStakes() == startStakes
    assert asc.sm.getStakes() == [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB, asc.BOB]
    staker  = stakers[1]
    idxs = [1]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 1, False)
    assert idxs == calcIdxs

    tx = asc.sm.unstake(idxs, {'from': staker})

    curNumStakes = 3
    assert asc.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB]
    assert asc.sm.getStakes() == newStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(asc, web3.eth.blockNumber, startStakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]


# Unstake 2 from the 3rd staker in stakedMultiSmall
def test_unstake_2_of_3rd_staker_from_stakedMultiSmall(asc, stakedMultiSmall):
    nums, stakers, startStakes = stakedMultiSmall
    assert len(startStakes) == 7
    assert asc.sm.getStakes() == [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB, asc.BOB]
    assert asc.sm.getStakes() == startStakes
    staker = stakers[2]
    idxs = [3, 4]
    calcIdxs, newStakes = getModStakes(startStakes, staker, 2, False)
    assert idxs == calcIdxs

    print(asc.sm.updateExecutor().return_value)
    print(web3.eth.blockNumber)
    tx = asc.sm.unstake(idxs, {'from': staker})

    curNumStakes = 0
    assert asc.sm.getTotalStaked() == (len(startStakes) - len(idxs)) * STAN_STAKE
    assert asc.sm.getStake(staker) == 0
    assert asc.sm.getStakes() == [asc.ALICE, asc.BOB, asc.BOB, asc.BOB, asc.BOB]
    assert asc.sm.getStakes() == newStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(asc, web3.eth.blockNumber, startStakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, len(idxs) * STAN_STAKE]