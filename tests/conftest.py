import pytest
from brownie import web3, chain
from consts import *
from utils import *


# Test isolation
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# Deploy the contracts for repeated tests without having to redeploy each time

def deploy_initial_ASC_contracts(ASCoin, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
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

    asc.ASC = asc.DEPLOYER.deploy(ASCoin, "Active Smart Contract Protocol", "ASC")
    asc.po = asc.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    asc.o = asc.DEPLOYER.deploy(Oracle, asc.po)
    asc.sm = asc.DEPLOYER.deploy(StakeManager, asc.o, asc.ASC)
    asc.vf = asc.DEPLOYER.deploy(Forwarder)
    asc.r = asc.DEPLOYER.deploy(
        Registry,
        asc.ASC,
        asc.sm,
        asc.o,
        asc.vf
    )
    asc.vf.setCaller(asc.r, True, asc.FR_DEPLOYER)
    asc.m = asc.DEPLOYER.deploy(
        Miner,
        asc.ASC,
        asc.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )

    return asc


@pytest.fixture(scope="module")
def cleanASC(ASCoin, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
    return deploy_initial_ASC_contracts(ASCoin, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner)


@pytest.fixture(scope="module")
def asc(cleanASC):
    asc = cleanASC
    # For enabling rewards
    asc.ASC.transfer(asc.m, INIT_ASC_REW_POOL, asc.FR_DEPLOYER)
    # For being able to test staking with
    asc.ASC.transfer(asc.ALICE, MAX_TEST_STAKE, asc.FR_DEPLOYER)
    asc.ASC.approve(asc.sm, MAX_TEST_STAKE, asc.FR_ALICE)
    asc.ASC.transfer(asc.BOB, MAX_TEST_STAKE, asc.FR_DEPLOYER)
    asc.ASC.approve(asc.sm, MAX_TEST_STAKE, asc.FR_BOB)
    asc.ASC.transfer(asc.CHARLIE, MAX_TEST_STAKE, asc.FR_DEPLOYER)
    asc.ASC.approve(asc.sm, MAX_TEST_STAKE, asc.FR_CHARLIE)

    return asc



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
def stakedMultiSmall(asc, evmMaths, stakedMin):
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

    # The executor won't change in future tests without changing epoch
    chain.mine(BLOCKS_IN_EPOCH)
    prevExec = asc.sm.getExecutor()
    prevStakes = asc.sm.getStakes()
    updateExecReturn = asc.sm.updateExecutor().return_value
    updateExecReturn = (prevExec, prevStakes, updateExecReturn, web3.eth.block_number, asc.sm.getTotalStaked(), asc.sm.getExecutor(), asc.sm.getStakes())

    totalNumStakes = 7
    stakes = [asc.ALICE, asc.BOB, asc.BOB, asc.CHARLIE, asc.CHARLIE, asc.BOB, asc.BOB]

    assert asc.sm.getTotalStaked() == totalNumStakes * STAN_STAKE
    assert asc.sm.getStakes() == stakes
    assert asc.sm.getCurEpoch() == getEpoch(web3.eth.block_number)
    newExec, epoch = getExecutor(evmMaths, web3.eth.block_number + 1, stakes)
    assert asc.sm.isUpdatedExec(newExec).return_value
    assert asc.sm.getExecutor() == (newExec, epoch)
    for addr in a:
        assert asc.sm.isCurExec(addr) == (addr == newExec)

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
    return asc.DEPLOYER.deploy(VulnerableStaker, asc.o.address, asc.ASC.address)


# Need to have already staked properly in order to test `noFish`
@pytest.fixture(scope="module")
def vulnerableStaked(asc, vulnerableStaker):
    staker = asc.ALICE
    asc.ASC.approve(vulnerableStaker, MAX_TEST_STAKE, {'from': staker})
    # *2 so that `unstake` doesn't fail because of an ERC20 transfer for STAN_STAKE
    vulnerableStaker.stake(2, {'from': staker})
    return vulnerableStaker, staker


# Need to set up a vulnerable Registry to test `noFish` since there's
# obviously intentionally no way of getting ETH out of Registry
# without ethForCall or paying the bounty in ETH
@pytest.fixture(scope="module")
def vulnerableRegistry(asc, VulnerableRegistry):
    return asc.DEPLOYER.deploy(
        VulnerableRegistry,
        asc.ASC,
        asc.sm,
        asc.o,
        asc.vf
    )


# Need to have some 'external' contract whose state needs changing in order
# to use ASC
@pytest.fixture(scope="module")
def mockTarget(asc, MockTarget, vulnerableRegistry):
    return asc.DEPLOYER.deploy(MockTarget, asc.vf, vulnerableRegistry)


# Need to test nonReentrant modifier
@pytest.fixture(scope="module")
def mockReentrancyAttack(asc, MockReentrancyAttack):
    return asc.DEPLOYER.deploy(MockReentrancyAttack, asc.r)


# Need to test gas usage with the exact same rounding profile that Solidity
# uses vs Python
@pytest.fixture(scope="module")
def evmMaths(asc, EVMMaths):
    x = asc.DEPLOYER.deploy(EVMMaths)
    print(x)
    print(type(x))
    return x


# Need to have some raw requests to test executeRawReq. Need a request that has ethForCall
# set to 0 and 1 that doesn't, and 1 that pays with ASC with ethForCall and 1 without
@pytest.fixture(scope="module")
def reqsRaw(asc, mockTarget):
    ethForCall = E_18
    msgValue = 1.5 * ethForCall

    callData = mockTarget.setX.encode_input(5)
    asc.r.newRawReq(mockTarget, asc.DENICE, callData, 0, False, False, {'from': asc.BOB, 'value': msgValue})
    reqNoEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, 0, False, False)

    callData = mockTarget.setXPay.encode_input(5)
    asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, False, {'from': asc.BOB, 'value': msgValue})
    reqEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, False, False)

    asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)

    callData = mockTarget.setX.encode_input(5)
    asc.r.newRawReq(mockTarget, asc.DENICE, callData, 0, False, True, {'from': asc.BOB})
    reqPayASCNoEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE.address, callData, 0, 0, False, True)

    callData = mockTarget.setXPay.encode_input(5)
    asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, True, {'from': asc.BOB, 'value': ethForCall})
    reqPayASCEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, False, True)

    callData = mockTarget.setAddrPayVerified.encode_input(asc.BOB)
    asc.r.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, True, True, {'from': asc.BOB, 'value': ethForCall})
    reqPayASCEthForCallVerifySender = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, True, True)

    return reqNoEthForCall, reqEthForCall, reqPayASCNoEthForCall, reqPayASCEthForCall, reqPayASCEthForCallVerifySender, msgValue, ethForCall


# Need to have some hashed requests to test executeHashedReq. Need a request that has ethForCall
# set to 0 and 1 that doesn't, and 1 that pays with ASC with ethForCall and 1 without
@pytest.fixture(scope="module")
def hashedReqs(asc, mockTarget):
    ethForCall = E_18
    msgValue = 1.5 * ethForCall

    callData = mockTarget.setX.encode_input(5)
    reqNoEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, 0, False, False)
    tx = asc.r.newHashedReq(mockTarget, asc.DENICE, callData, 0, False, False, *getIpfsMetaData(asc, reqNoEthForCall), {'from': asc.BOB, 'value': msgValue})

    callData = mockTarget.setXPay.encode_input(5)
    reqEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, False, False)
    tx = asc.r.newHashedReq(mockTarget, asc.DENICE, callData, ethForCall, False, False, *getIpfsMetaData(asc, reqEthForCall), {'from': asc.BOB, 'value': msgValue})

    asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
    
    callData = mockTarget.setX.encode_input(5)
    reqPayASCNoEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    tx = asc.r.newHashedReq(mockTarget, asc.DENICE, callData, 0, False, True, *getIpfsMetaData(asc, reqPayASCNoEthForCall), {'from': asc.BOB, 'value': 0})

    callData = mockTarget.setXPay.encode_input(5)
    reqPayASCEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, False, True)
    tx = asc.r.newHashedReq(mockTarget, asc.DENICE, callData, ethForCall, False, True, *getIpfsMetaData(asc, reqPayASCEthForCall), {'from': asc.BOB, 'value': ethForCall})

    callData = mockTarget.setAddrPayVerified.encode_input(asc.BOB)
    reqPayASCEthForCallVerifySender = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, True, True)
    tx = asc.r.newHashedReq(mockTarget, asc.DENICE, callData, ethForCall, True, True, *getIpfsMetaData(asc, reqPayASCEthForCall), {'from': asc.BOB, 'value': ethForCall})

    reqs = [reqNoEthForCall, reqEthForCall, reqPayASCNoEthForCall, reqPayASCEthForCall, reqPayASCEthForCallVerifySender]
    reqHashes = [bytesToHex(addReqGetHashBytes(asc, r)) for r in reqs]

    return reqs, reqHashes, msgValue, ethForCall


# With hashReqNoEth, we can't send eth in the call and have to pay via ASC, so
# only one combination this time
@pytest.fixture(scope="module")
def hashedReqUnveri(asc, mockTarget):
    asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)

    tx = asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    return req, reqHashBytes


# Need to have already staked and have new requests already made so that execute
# can be tested with and without payWithASC for each type
@pytest.fixture(scope="module")
def vulnerableReqsRaw(asc, mockTarget, vulnerableRegistry, stakedMin):
    ethForCall = E_18
    msgValue = 1.5 * ethForCall

    callData = mockTarget.callVulnerableTransfer.encode_input(asc.DENICE, 1)
    vulnerableRegistry.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, False, {'from': asc.BOB, 'value': msgValue})
    reqEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, False, False)

    asc.ASC.approve(vulnerableRegistry, MAX_TEST_STAKE, asc.FR_BOB)

    vulnerableRegistry.newRawReq(mockTarget, asc.DENICE, callData, ethForCall, False, True, {'from': asc.BOB, 'value': ethForCall})
    reqPayASCEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, False, True)

    return reqEthForCall, reqPayASCEthForCall, msgValue, ethForCall


# Need to have already staked and have new requests already made so that execute
# can be tested with and without payWithASC for each type
@pytest.fixture(scope="module")
def vulnerableHashedReqs(asc, mockTarget, vulnerableRegistry, stakedMin):
    ethForCall = E_18
    msgValue = 1.5 * ethForCall

    callData = mockTarget.callVulnerableTransfer.encode_input(asc.DENICE, 1)
    reqEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, msgValue, ethForCall, False, False)
    tx = vulnerableRegistry.newHashedReq(mockTarget, asc.DENICE, callData, ethForCall, False, False, *getIpfsMetaData(asc, reqEthForCall), {'from': asc.BOB, 'value': msgValue})

    asc.ASC.approve(vulnerableRegistry, MAX_TEST_STAKE, asc.FR_BOB)

    reqPayASCEthForCall = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, ethForCall, ethForCall, False, True)
    tx = vulnerableRegistry.newHashedReq(mockTarget, asc.DENICE, callData, ethForCall, False, True, *getIpfsMetaData(asc, reqPayASCEthForCall), {'from': asc.BOB, 'value': ethForCall})

    reqs = [reqEthForCall, reqPayASCEthForCall]
    reqHashes = [bytesToHex(addReqGetHashBytes(asc, r)) for r in reqs]

    return reqs, reqHashes, msgValue, ethForCall


# Need to have already staked and have new requests already made so that execute
# can be tested with and without payWithASC for each type
@pytest.fixture(scope="module")
def vulnerableHashedReqUnveri(asc, mockTarget, vulnerableRegistry, stakedMin):
    # Send it ETH so that there is ETH to steal
    asc.DEPLOYER.transfer(vulnerableRegistry, 1)
    asc.ASC.approve(vulnerableRegistry, MAX_TEST_STAKE, asc.FR_BOB)
    callData = mockTarget.callVulnerableTransfer.encode_input(asc.DENICE, 1)
    req = (asc.BOB.address, mockTarget.address, asc.DENICE, callData, 0, 0, False, True)
    reqHashBytes = addReqGetHashBytes(asc, req)

    tx = vulnerableRegistry.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

    return req, reqHashBytes


# For testing Miner
@pytest.fixture(scope="module")
def freshMiner(a, asc, Miner):
    return a[0].deploy(
        Miner,
        asc.ASC,
        asc.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )