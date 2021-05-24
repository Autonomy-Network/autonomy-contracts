from consts import *
from utils import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy


# updateExecutor should do nothing if there's nothing staked
def test_updateExecutor_no_stake_do_nothing(a, asc):
    assert asc.sm.getTotalStaked() == 0
    assert asc.sm.getExecutor() == NULL_EXEC
    for addr in a:
        assert asc.sm.isCurExec(addr)

    tx = asc.sm.updateExecutor(asc.FR_ALICE)

    assert tx.return_value == (getEpoch(web3.eth.block_number), 0, 0, ADDR_0)
    assert asc.sm.getExecutor() == NULL_EXEC
    for addr in a:
        assert asc.sm.isCurExec(addr)
    assert asc.sm.isUpdatedExec(addr).return_value


def test_updateExecutor_stakedMin(asc, evmMaths, stakedMin):
    numStanStakes, staker, tx = stakedMin
    assert asc.sm.getTotalStaked() == numStanStakes * STAN_STAKE
    assert asc.sm.getExecutor() == getExecutor(evmMaths, web3.eth.block_number, [staker])
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == staker)


# updateExecutor should do nothing if the epoch hasn't changed
def test_updateExecutor_same_epoch(a, asc, evmMaths, stakedMin):
    numStanStakes, staker, tx = stakedMin
    # Make sure we're on block number xxx99 so that updateExecutor will be called
    # at the start of the next epoch and we can test every single block in the epoch
    chain.mine(BLOCKS_IN_EPOCH - (web3.eth.block_number % BLOCKS_IN_EPOCH) - 1)
    assert web3.eth.block_number % BLOCKS_IN_EPOCH == BLOCKS_IN_EPOCH - 1

    # Ensure the current executor is set at the start of the epoch
    tx = asc.sm.updateExecutor(asc.FR_ALICE)

    assert web3.eth.block_number % BLOCKS_IN_EPOCH == 0
    assert tx.return_value == getUpdatedExecResult(evmMaths, web3.eth.block_number, [staker])
    assert asc.sm.isUpdatedExec(staker).return_value
    assert asc.sm.getExecutor() == (staker, getEpoch(web3.eth.block_number))
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == staker)
    
    # Make Bob the only one with stake in the contract to ensure that if updateExecutor
    # called such that it changed executor, it would change to Bob
    asc.sm.unstake([i for i in range(numStanStakes)], asc.FR_ALICE)
    
    staker2 = asc.BOB
    assert asc.sm.isUpdatedExec(staker).return_value
    assert asc.sm.isUpdatedExec(staker2).return_value
    assert asc.sm.getExecutor() == (staker, getEpoch(web3.eth.block_number))
    # isCurExec always true when no stake
    for addr in a:
        assert asc.sm.isCurExec(addr)
    
    asc.sm.stake(INIT_NUM_STAKES, asc.FR_BOB)

    assert asc.sm.isUpdatedExec(staker).return_value
    assert not asc.sm.isUpdatedExec(staker2).return_value
    assert asc.sm.getExecutor() == (staker, getEpoch(web3.eth.block_number))
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == staker)

    stakes = [staker2] * INIT_NUM_STAKES
    assert asc.sm.getStakes() == stakes
    assert asc.sm.getStakesLength() == len(stakes)
    # Should revert if requesting an index that is above the max
    with reverts():
        asc.sm.getStakesSlice(0, len(stakes) + 1)
    assert asc.sm.getStakesSlice(0, len(stakes)) == stakes

    # Make sure that updateExecutor doesn't change the executor for every remaining block in the epoch
    while web3.eth.block_number % BLOCKS_IN_EPOCH != 99:
        assert asc.sm.updateExecutor(asc.FR_ALICE).return_value == (getEpoch(web3.eth.block_number), 0, 0, ADDR_0)
        assert asc.sm.getExecutor() == (staker, getEpoch(web3.eth.block_number))
        for addr in a:
            assert asc.sm.isCurExec(addr) == (addr == staker)
    
    # Check that it does change the executor to Bob in the next block
    assert web3.eth.block_number % BLOCKS_IN_EPOCH == 99
    
    tx = asc.sm.updateExecutor(asc.FR_ALICE)
    
    assert tx.return_value == getUpdatedExecResult(evmMaths, web3.eth.block_number, stakes)
    assert web3.eth.block_number % BLOCKS_IN_EPOCH == 0
    assert asc.sm.getExecutor() == (staker2, getEpoch(web3.eth.block_number))
    assert not asc.sm.isUpdatedExec(staker).return_value
    assert asc.sm.isUpdatedExec(staker2).return_value
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == staker2)


def test_updateExecutor_stakedMulti(asc, evmMaths, stakedMulti):
    stakes = asc.sm.getStakes()
    for i in range(BLOCKS_IN_EPOCH * 2):
        tx = asc.sm.updateExecutor(asc.FR_ALICE)

        exec, epoch = getExecutor(evmMaths, web3.eth.block_number, stakes)
        assert asc.sm.getExecutor() == (exec, epoch)
        if web3.eth.block_number % BLOCKS_IN_EPOCH == 0:
            assert tx.return_value == getUpdatedExecResult(evmMaths, web3.eth.block_number, stakes)
        else:
            assert tx.return_value == (epoch, 0, 0, ADDR_0)
        for addr in a:
            assert asc.sm.isCurExec(addr) == (addr == exec)


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_updateExecutor_rev_noFish_same_epoch(asc, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    vStaker.updateExecutor(asc.FR_ALICE)
    vStaker.vulnerableTransfer(asc.DENICE, amount)

    with reverts(REV_MSG_NOFISH):
        vStaker.updateExecutor(asc.FR_ALICE)


@given(amount=strategy('uint256', max_value=STAN_STAKE-1, exclude=0))
def test_updateExecutor_rev_noFish_different_epoch(asc, vulnerableStaked, amount):
    vStaker, staker = vulnerableStaked
    vStaker.updateExecutor(asc.FR_ALICE)
    vStaker.vulnerableTransfer(asc.DENICE, amount)
    chain.mine(BLOCKS_IN_EPOCH)

    with reverts(REV_MSG_NOFISH):
        vStaker.updateExecutor(asc.FR_ALICE)