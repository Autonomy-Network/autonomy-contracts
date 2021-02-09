import pytest
from brownie import web3, chain
from consts import *
from utils import *



# Test isolation
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Deploy the contracts for repeated tests without having to redeploy each time

def deploy_initial_ASC_contracts(ASCoin, Oracle, StakeManager, Registry):
    class Context:
        pass

    asc = Context()
    # It's a bit easier to not get mixed up with accounts if they're named
    # Can't define this in consts because a needs to be imported into the test
    asc.DEPLOYER = a[0]
    asc.FR_DEPLOYER = {"from": asc.DEPLOYER}
    asc.ALICE = a[1]
    asc.FR_ALICE = {"from": asc.ALICE}
    asc.BOB = a[2]
    asc.FR_BOB = {"from": asc.BOB}
    asc.CHARLIE = a[3]
    asc.FR_CHARLIE = {"from": asc.CHARLIE}
    asc.DENICE = a[4]
    asc.FR_DENICE = {"from": asc.DENICE}


    # Calling `updateExecutor` requires the epoch to be > 0
    chain.mine(BLOCKS_IN_EPOCH)

    asc.ASCoin = asc.DEPLOYER.deploy(ASCoin, "Active Smart Contract Protocol", "ASC")
    asc.oracle = asc.DEPLOYER.deploy(Oracle)
    asc.sm = asc.DEPLOYER.deploy(StakeManager, asc.oracle.address, asc.ASCoin.address)
    asc.r = asc.DEPLOYER.deploy(Registry, asc.sm.address, MAX_REW_PER_ASC)

    asc.ASCoin.transfer(asc.ALICE, MAX_TEST_STAKE, {'from': asc.DEPLOYER})
    asc.ASCoin.approve(asc.sm, MAX_TEST_STAKE, {'from': asc.ALICE})
    asc.ASCoin.transfer(asc.BOB, MAX_TEST_STAKE, {'from': asc.DEPLOYER})
    asc.ASCoin.approve(asc.sm, MAX_TEST_STAKE, {'from': asc.BOB})
    asc.ASCoin.transfer(asc.CHARLIE, MAX_TEST_STAKE, {'from': asc.DEPLOYER})
    asc.ASCoin.approve(asc.sm, MAX_TEST_STAKE, {'from': asc.CHARLIE})

    return asc


@pytest.fixture(scope="module")
def asc(ASCoin, Oracle, StakeManager, Registry):
    return deploy_initial_ASC_contracts(ASCoin, Oracle, StakeManager, Registry)


@pytest.fixture(scope="module")
def stakedMin(asc):
    staker = asc.ALICE
    numStakes = 1
    assert asc.sm.getTotalStaked() == 0

    tx = asc.sm.stake(numStakes, {'from': staker})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    asc.sm.updateExecutor()

    return numStakes, staker, tx


@pytest.fixture(scope="module")
def stakedHigh(asc):
    staker = asc.ALICE
    numStakes = INIT_NUM_STAKES

    tx = asc.sm.stake(numStakes, {'from': staker})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    asc.sm.updateExecutor()

    return numStakes, staker, tx


@pytest.fixture(scope="module")
def stakedMultiSmall(asc, stakedMin):
    _, staker0, tx0 = stakedMin
    num0 = 1

    num1 = 2
    tx1 = asc.sm.stake(num1, {'from': asc.BOB})
    assert asc.sm.getStake(asc.BOB) == num1 * STAN_STAKE

    num2 = 2
    tx2 = asc.sm.stake(num2, {'from': asc.CHARLIE})
    assert asc.sm.getStake(asc.CHARLIE) == num2 * STAN_STAKE

    num3 = 2
    tx3 = asc.sm.stake(num3, {'from': asc.BOB})
    assert asc.sm.getStake(asc.BOB) == (num1 + num3) * STAN_STAKE
    print(f'stakedMultiSmall last stake block num = {tx3.block_number}')

    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    prevExec = asc.sm.getExecutor()
    prevStakes = asc.sm.getStakes()
    updateExecReturn = asc.sm.updateExecutor().return_value
    updateExecReturn = (prevExec, prevStakes, updateExecReturn, web3.eth.blockNumber, asc.sm.getTotalStaked(), asc.sm.getExecutor(), asc.sm.getStakes())

    totalNumStakes = 7
    stakes = [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB, asc.BOB]

    assert asc.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == stakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.blockNumber)
    newExec, epoch = getExecutor(asc, web3.eth.blockNumber, stakes)
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)

    print(f'stakedMultiSmall last block num = {web3.eth.blockNumber}')

    return (num0, num1, num2, num3), (asc.ALICE, asc.BOB, asc.CHARLIE, asc.BOB), stakes, updateExecReturn


@pytest.fixture(scope="module")
def stakedMulti(asc, stakedMin):
    _, staker0, tx0 = stakedMin
    num0 = 1
    num1 = 4
    num2 = 69 # Nice
    num3 = 20
    tx1 = asc.sm.stake(num1, {'from': asc.BOB})
    tx2 = asc.sm.stake(num2, {'from': asc.CHARLIE})
    tx3 = asc.sm.stake(num3, {'from': asc.BOB})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    asc.sm.updateExecutor()

    return (num0, num1, num2, num3), (asc.ALICE, asc.BOB, asc.CHARLIE, asc.BOB), (tx0, tx1, tx2, tx3)


# Need to set up a vulnerable StakeManager to test `noFish` since there's
# obviously intentionally no way of getting ASCoin out of StakeManager
# without unstaking
@pytest.fixture(scope="module")
def vulnerableStaker(asc, VulnerableStaker):
    return asc.DEPLOYER.deploy(VulnerableStaker, asc.oracle.address, asc.ASCoin.address)


# Need to have already staked properly in order to test `noFish`
@pytest.fixture(scope="module")
def vulnerableStaked(asc, vulnerableStaker):
    staker = asc.ALICE
    asc.ASCoin.approve(vulnerableStaker, MAX_TEST_STAKE, {'from': staker})
    # *2 so that `unstake` doesn't fail because of an ERC20 transfer for STAN_STAKE
    vulnerableStaker.stake(2, {'from': staker})
    return vulnerableStaker, staker


# Need to have already staked properly in order to test `noFish`
@pytest.fixture(scope="module")
def mockTarget(asc, MockTarget):
    return asc.DEPLOYER.deploy(MockTarget)