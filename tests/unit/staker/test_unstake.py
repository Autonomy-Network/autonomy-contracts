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
    startStakeIdxs,
    startStakes
):
    assert asc.sm.getTotalStaked() == startTotalNumStakes * STAN_STAKE
    assert asc.sm.getStake(staker) == maxNumStakes * STAN_STAKE
    assert asc.sm.getStakeIdxs(staker) == startStakeIdxs
    assert asc.sm.getStakes() == startStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    assert asc.sm.getExecutor() == getExecutor(web3.eth.blockNumber, startStakes) 
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == curExec)
    
    if numStakes == 0:
        with reverts(REV_MSG_NZ_UINT):
            asc.sm.unstake(numStakes, {'from': staker})
    elif numStakes < maxNumStakes:
        tx = asc.sm.unstake(numStakes, {'from': staker})

        assert asc.sm.getTotalStaked() == (startTotalNumStakes - numStakes) * STAN_STAKE
        assert asc.sm.getStake(staker) == (maxNumStakes - numStakes) * STAN_STAKE
        assert asc.sm.getStakeIdxs(staker) == startStakeIdxs[:-numStakes]
        newStakes = getModStakes(startStakes, staker, numStakes, False)
        assert asc.sm.getStakes() == getModStakes(startStakes, staker, numStakes, False)
        assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
        newExec, epoch = getExecutor(web3.eth.blockNumber, startStakes)
        assert asc.sm.getExecutor() == (newExec, epoch)
        for addr in a:
            assert asc.sm.isCurExec(addr) == (addr == newExec)
        assert tx.events["Unstaked"][0].values() == [staker, numStakes * STAN_STAKE]
    else:
        with reverts(REV_MSG_EXCEED_BAL):
            asc.sm.unstake(numStakes, {'from': staker})



@given(numStakes=strategy('uint256', max_value=INIT_NUM_STAKES))
def test_unstake(asc, web3, stakedHigh, numStakes):
    _, staker, _ = stakedHigh
    unstakeTest(
        asc,
        web3,
        numStakes,
        staker,
        staker,
        INIT_NUM_STAKES,
        INIT_NUM_STAKES,
        [i for i in range(INIT_NUM_STAKES)],
        [staker] * INIT_NUM_STAKES
    )


# # Want to have a could tests with specific, manual values because it's
# # possible that some of the more complex algorithms in StakeManager have
# # errors and I've just replicated those errors in things like getModStakes()
# def test_unstake_7(asc, web3, stakedHigh):
#     startNumStakes, staker, _ = stakedHigh
#     tx = asc.sm.unstake(numStakes, {'from': staker})

#     curNumStakes = startNumStakes - 7
#     assert asc.sm.getTotalStaked() == curNumStakes * STAN_STAKE
#     assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
#     assert asc.sm.getStakeIdxs(staker) == [i for i in range(curNumStakes)]
#     assert asc.sm.getStakes() == [staker] * curNumStakes
#     assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
#     newExec, epoch = getExecutor(web3.eth.blockNumber, startStakes)
#     assert asc.sm.getExecutor() == (newExec, epoch)
#     for addr in a:
#         assert asc.sm.isCurExec(addr) == (addr == newExec)
#     assert tx.events["Unstaked"][0].values() == [staker, numStakes * STAN_STAKE]


# Want to have a couple tests with specific, manual values because it's
# possible that some of the more complex algorithms in StakeManager have
# errors and I've just replicated those errors in things like getModStakes()
def test_unstake_7(asc, web3, stakedHigh):
    startNumStakes, staker, _ = stakedHigh
    stakesToRemove = 7
    tx = asc.sm.unstake(stakesToRemove, {'from': staker})

    curNumStakes = startNumStakes - stakesToRemove
    assert asc.sm.getTotalStaked() == curNumStakes * STAN_STAKE
    assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
    assert asc.sm.getStakeIdxs(staker) == [i for i in range(curNumStakes)]
    assert asc.sm.getStakes() == [staker] * curNumStakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(web3.eth.blockNumber, [staker] * startNumStakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)
    assert tx.events["Unstaked"][0].values() == [staker, stakesToRemove * STAN_STAKE]


# # Unstake 1 from the 2nd staker in stakedMultiSmall
# def test_unstake_1_of_2nd_staker_from_stakedMultiSmall(asc, web3, stakedMultiSmall):
#     nums, stakers, stakes = stakedMultiSmall
#     totalNums = sum(nums)
#     startNumStakes, staker, _ = nums[1], stakers[1]
#     numToRemove = 1
#     tx = asc.sm.unstake(numStakes, {'from': staker})

#     curNumStakes = 1
#     assert asc.sm.getTotalStaked() == (totalNums - numToRemove) * STAN_STAKE
#     assert asc.sm.getStake(staker) == curNumStakes * STAN_STAKE
#     assert asc.sm.getStakeIdxs(staker) == []
#     assert asc.sm.getStakes() == [staker] * curNumStakes
#     assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
#     newExec, epoch = getExecutor(web3.eth.blockNumber, startStakes)
#     assert asc.sm.getExecutor() == (newExec, epoch)
#     for addr in a:
#         assert asc.sm.isCurExec(addr) == (addr == newExec)
#     assert tx.events["Unstaked"][0].values() == [staker, numStakes * STAN_STAKE]
