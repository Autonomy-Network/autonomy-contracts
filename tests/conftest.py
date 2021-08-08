import pytest
from brownie import web3, chain
from consts import *
from utils import *


# Test isolation
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Deploy the contracts for repeated tests without having to redeploy each time

def deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
    class Context:
        pass

    auto = Context()
    # It's a bit easier to not get mixed up with accounts if they're named
    # Can't define this in consts because a needs to be imported into the test
    auto.DEPLOYER = a[0]
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}
    auto.ALICE = a[1]
    auto.FR_ALICE = {"from": auto.ALICE}
    auto.BOB = a[2]
    auto.FR_BOB = {"from": auto.BOB}
    auto.CHARLIE = a[3]
    auto.FR_CHARLIE = {"from": auto.CHARLIE}
    auto.DENICE = a[4]
    auto.FR_DENICE = {"from": auto.DENICE}


    # Calling `updateExecutor` requires the epoch to be > 0
    chain.mine(BLOCKS_IN_EPOCH)

    auto.AUTO = auto.DEPLOYER.deploy(AUTO, "Autonomy Network", "AUTO")
    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, auto.AUTO)
    auto.uf = auto.DEPLOYER.deploy(Forwarder)
    auto.gf = auto.DEPLOYER.deploy(Forwarder)
    auto.ugf = auto.DEPLOYER.deploy(Forwarder)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.AUTO,
        auto.sm,
        auto.o,
        auto.uf,
        auto.gf,
        auto.ugf
    )
    auto.uf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.gf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.ugf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.m = auto.DEPLOYER.deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )

    return auto


@pytest.fixture(scope="module")
def cleanAUTO(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
    return deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner)


@pytest.fixture(scope="module")
def auto(cleanAUTO):
    auto = cleanAUTO
    # For enabling rewards
    auto.AUTO.transfer(auto.m, INIT_AUTO_REW_POOL, auto.FR_DEPLOYER)
    # For being able to test staking with
    auto.AUTO.transfer(auto.ALICE, MAX_TEST_STAKE, auto.FR_DEPLOYER)
    auto.AUTO.approve(auto.sm, MAX_TEST_STAKE, auto.FR_ALICE)
    auto.AUTO.transfer(auto.BOB, MAX_TEST_STAKE, auto.FR_DEPLOYER)
    auto.AUTO.approve(auto.sm, MAX_TEST_STAKE, auto.FR_BOB)
    auto.AUTO.transfer(auto.CHARLIE, MAX_TEST_STAKE, auto.FR_DEPLOYER)
    auto.AUTO.approve(auto.sm, MAX_TEST_STAKE, auto.FR_CHARLIE)

    return auto



@pytest.fixture(scope="module")
def stakedMin(auto):
    staker = auto.ALICE
    numStakes = 1
    assert auto.sm.getTotalStaked() == 0

    tx = auto.sm.stake(numStakes, {'from': staker})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    auto.sm.updateExecutor()

    return numStakes, staker, tx


@pytest.fixture(scope="module")
def stakedHigh(auto):
    staker = auto.ALICE
    numStakes = INIT_NUM_STAKES

    tx = auto.sm.stake(numStakes, {'from': staker})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    auto.sm.updateExecutor()

    return numStakes, staker, tx


@pytest.fixture(scope="module")
def stakedMultiSmall(auto, evmMaths, stakedMin):
    _, staker0, tx0 = stakedMin
    num0 = 1

    num1 = 2
    tx1 = auto.sm.stake(num1, {'from': auto.BOB})
    assert auto.sm.getStake(auto.BOB) == num1 * STAN_STAKE

    num2 = 2
    tx2 = auto.sm.stake(num2, {'from': auto.CHARLIE})
    assert auto.sm.getStake(auto.CHARLIE) == num2 * STAN_STAKE

    num3 = 2
    tx3 = auto.sm.stake(num3, {'from': auto.BOB})
    assert auto.sm.getStake(auto.BOB) == (num1 + num3) * STAN_STAKE

    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    updateExecReturn = auto.sm.updateExecutor().return_value

    totalNumStakes = 7
    stakes = [auto.ALICE, auto.BOB, auto.BOB, auto.CHARLIE, auto.CHARLIE, auto.BOB, auto.BOB]

    assert auto.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert auto.sm.getStakes() == stakes
    assert auto.sm.getCurEpoch() == getEpoch(bn())
    newExec, epoch = getExecutor(evmMaths, bn() + 1, stakes, None)
    assert auto.sm.isUpdatedExec(newExec).return_value
    assert auto.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert auto.sm.isCurExec(addr) == (addr == newExec)

    return (num0, num1, num2, num3), (auto.ALICE, auto.BOB, auto.CHARLIE, auto.BOB), stakes, updateExecReturn


@pytest.fixture(scope="module")
def stakedMulti(auto, stakedMin):
    _, staker0, tx0 = stakedMin
    num0 = 1
    num1 = 4
    num2 = 69 # Nice
    num3 = 20
    tx1 = auto.sm.stake(num1, {'from': auto.BOB})
    tx2 = auto.sm.stake(num2, {'from': auto.CHARLIE})
    tx3 = auto.sm.stake(num3, {'from': auto.BOB})
    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    auto.sm.updateExecutor()

    return (num0, num1, num2, num3), (auto.ALICE, auto.BOB, auto.CHARLIE, auto.BOB), (tx0, tx1, tx2, tx3)


# Need to set up a vulnerable StakeManager to test `noFish` since there's
# obviously intentionally no way of getting AUTO out of StakeManager
# without unstaking
@pytest.fixture(scope="module")
def vulnerableStaker(auto, VulnerableStaker):
    return auto.DEPLOYER.deploy(VulnerableStaker, auto.o.address, auto.AUTO.address)


# Need to have already staked properly in order to test `noFish`
@pytest.fixture(scope="module")
def vulnerableStaked(auto, vulnerableStaker):
    staker = auto.ALICE
    auto.AUTO.approve(vulnerableStaker, MAX_TEST_STAKE, {'from': staker})
    # *2 so that `unstake` doesn't fail because of an ERC20 transfer for STAN_STAKE
    vulnerableStaker.stake(2, {'from': staker})
    return vulnerableStaker, staker


# Need to set up a vulnerable Registry to test `noFish` since there's
# obviously intentionally no way of getting ETH out of Registry
# without ethForCall or paying the bounty in ETH
@pytest.fixture(scope="module")
def vulnerableRegistry(auto, VulnerableRegistry):
    return auto.DEPLOYER.deploy(
        VulnerableRegistry,
        auto.AUTO,
        auto.sm,
        auto.o,
        auto.uf,
        auto.gf,
        auto.ugf
    )


# Need to have some 'external' contract whose state needs changing in order
# to use AUTO
@pytest.fixture(scope="module")
def mockTarget(auto, MockTarget, vulnerableRegistry):
    return auto.DEPLOYER.deploy(MockTarget, auto.uf, auto.gf, auto.ugf, auto.r, vulnerableRegistry)


# Need to test nonReentrant modifier
@pytest.fixture(scope="module")
def mockReentrancyAttack(auto, MockReentrancyAttack):
    return auto.DEPLOYER.deploy(MockReentrancyAttack, auto.r)


# Need to test gas usage with the exact same rounding profile that Solidity
# uses vs Python
@pytest.fixture(scope="module")
def evmMaths(cleanAUTO, EVMMaths):
    x = cleanAUTO.DEPLOYER.deploy(EVMMaths)
    return x


# Need to have some requests to test executeHashedReq. Need a request that has ethForCall
# set to 0 and 1 that doesn't, and 1 that pays with AUTO with ethForCall and 1 without
@pytest.fixture(scope="module")
def hashedReqs(auto, mockTarget):
    ethForCall = E_18
    msgValue = int(1.5 * ethForCall)
    reqs = []

    # Set a var on a target without sending ETH with the call, pay upfront
    callData = mockTarget.setX.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, 0, False, False, False))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, 0, False, False, False, {'from': auto.BOB, 'value': msgValue})

    # Set a var on a target, sending ETH with the call, pay upfront
    callData = mockTarget.setXPay.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, False, False))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, False, False, {'from': auto.BOB, 'value': msgValue})

    auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
    
    # Set a var on a target, paying with AUTO after execution
    callData = mockTarget.setX.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, 0, False, False, True, {'from': auto.BOB, 'value': 0})

    # Set a var on a target, sending ETH witht the call, paying with AUTO after execution
    callData = mockTarget.setXPay.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, False, True))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, False, True, {'from': auto.BOB, 'value': ethForCall})

    # Set an address that is the original users' address on a target, pay with AUTO after execution
    callData = mockTarget.setAddrPayUserVerified.encode_input(auto.BOB)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, True, False, True))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, True, False, True, {'from': auto.BOB, 'value': ethForCall})

    # Set a var that is the gas the execution charges for, sending ETH with the call, pay with AUTO after execution
    callData = mockTarget.setXPayFeeVerified.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, True, True))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, True, True, {'from': auto.BOB, 'value': ethForCall})

    # Set a var that is the user's address and the gas the execution charges for, pay for execution with ETH sent from the target
    callData = mockTarget.setAddrXPayUserFeeVerifiedSendEth.encode_input(auto.BOB, 5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, True, True, False))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, 0, True, True, False, {'from': auto.BOB, 'value': 0})

    # Set a var that is the user's address and the gas the execution charges for, send ETH with call, pay with AUTO 
    callData = mockTarget.setAddrXPayUserFeeVerified.encode_input(auto.BOB, 5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, True, True, True))
    tx = auto.r.newReq(mockTarget, auto.DENICE, callData, ethForCall, True, True, True, {'from': auto.BOB, 'value': ethForCall})

    reqHashes = [keccakReq(auto, r) for r in reqs]

    return reqs, reqHashes, msgValue, ethForCall


# With hashReqNoEth, we can't send eth in the call and have to pay via AUTO, so
# only one combination this time
@pytest.fixture(scope="module")
def hashedReqUnveri(auto, mockTarget):
    auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True)
    reqHashBytes = addReqGetHashBytes(auto, req)

    tx = auto.r.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    return req, reqHashBytes


# Need to have already staked and have new requests already made so that execute
# can be tested with and without payWithAUTO for each type
@pytest.fixture(scope="module")
def vulnerableHashedReqs(auto, mockTarget, vulnerableRegistry, stakedMin):
    ethForCall = E_18
    msgValue = int(1.5 * ethForCall)

    callData = mockTarget.callVulnerableTransfer.encode_input(auto.DENICE, 1)
    reqEthForCall = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, False, False)
    tx = vulnerableRegistry.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, False, False, {'from': auto.BOB, 'value': msgValue})

    auto.AUTO.approve(vulnerableRegistry, MAX_TEST_STAKE, auto.FR_BOB)

    reqPayAUTOEthForCall = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, False, True)
    tx = vulnerableRegistry.newReq(mockTarget, auto.DENICE, callData, ethForCall, False, False, True, {'from': auto.BOB, 'value': ethForCall})

    reqs = [reqEthForCall, reqPayAUTOEthForCall]
    reqHashes = [bytesToHex(addReqGetHashBytes(auto, r)) for r in reqs]

    return reqs, reqHashes, msgValue, ethForCall


# Need to have already staked and have new requests already made so that execute
# can be tested with and without payWithAUTO for each type
@pytest.fixture(scope="module")
def vulnerableHashedReqUnveri(auto, mockTarget, vulnerableRegistry, stakedMin):
    # Send it ETH so that there is ETH to steal
    auto.DEPLOYER.transfer(vulnerableRegistry, 1)
    auto.AUTO.approve(vulnerableRegistry, MAX_TEST_STAKE, auto.FR_BOB)
    callData = mockTarget.callVulnerableTransfer.encode_input(auto.DENICE, 1)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True)
    reqHashBytes = addReqGetHashBytes(auto, req)

    tx = vulnerableRegistry.newHashedReqUnveri(reqHashBytes, {'from': auto.BOB, 'value': 0})

    return req, reqHashBytes


# For testing Miner
@pytest.fixture(scope="module")
def freshMiner(a, auto, Miner):
    return a[0].deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )