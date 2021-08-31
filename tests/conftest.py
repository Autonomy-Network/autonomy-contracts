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
    auto.EOAs = list(a)[:10]
    auto.EOAsStr = [str(acc) for acc in auto.EOAs]

    # Calling `updateExecutor` requires the epoch to be > 0
    chain.mine(BLOCKS_IN_EPOCH)

    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po, False)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o)
    auto.uf = auto.DEPLOYER.deploy(Forwarder)
    auto.ff = auto.DEPLOYER.deploy(Forwarder)
    auto.uff = auto.DEPLOYER.deploy(Forwarder)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.sm,
        auto.o,
        auto.uf,
        auto.ff,
        auto.uff,
        "Autonomy Network",
        "AUTO",
        INIT_AUTO_SUPPLY
    )
    auto.AUTO = AUTO.at(auto.r.getAUTOAddr())
    auto.sm.setAUTO(auto.AUTO, auto.FR_DEPLOYER)
    auto.uf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.ff.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.uff.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.m = auto.DEPLOYER.deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )
    auto.all = [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m]
    auto.allStr = [str(x) for x in auto.all]

    return auto



@pytest.fixture(scope="module")
def cleanAUTO(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner):
    ERC1820_DEPLOYER = '0xa990077c3205cbDf861e17Fa532eeB069cE9fF96'
    ERC1820_PAYLOAD = '0xf90a388085174876e800830c35008080b909e5608060405234801561001057600080fd5b506109c5806100206000396000f3fe608060405234801561001057600080fd5b50600436106100a5576000357c010000000000000000000000000000000000000000000000000000000090048063a41e7d5111610078578063a41e7d51146101d4578063aabbb8ca1461020a578063b705676514610236578063f712f3e814610280576100a5565b806329965a1d146100aa5780633d584063146100e25780635df8122f1461012457806365ba36c114610152575b600080fd5b6100e0600480360360608110156100c057600080fd5b50600160a060020a038135811691602081013591604090910135166102b6565b005b610108600480360360208110156100f857600080fd5b5035600160a060020a0316610570565b60408051600160a060020a039092168252519081900360200190f35b6100e06004803603604081101561013a57600080fd5b50600160a060020a03813581169160200135166105bc565b6101c26004803603602081101561016857600080fd5b81019060208101813564010000000081111561018357600080fd5b82018360208201111561019557600080fd5b803590602001918460018302840111640100000000831117156101b757600080fd5b5090925090506106b3565b60408051918252519081900360200190f35b6100e0600480360360408110156101ea57600080fd5b508035600160a060020a03169060200135600160e060020a0319166106ee565b6101086004803603604081101561022057600080fd5b50600160a060020a038135169060200135610778565b61026c6004803603604081101561024c57600080fd5b508035600160a060020a03169060200135600160e060020a0319166107ef565b604080519115158252519081900360200190f35b61026c6004803603604081101561029657600080fd5b508035600160a060020a03169060200135600160e060020a0319166108aa565b6000600160a060020a038416156102cd57836102cf565b335b9050336102db82610570565b600160a060020a031614610339576040805160e560020a62461bcd02815260206004820152600f60248201527f4e6f7420746865206d616e616765720000000000000000000000000000000000604482015290519081900360640190fd5b6103428361092a565b15610397576040805160e560020a62461bcd02815260206004820152601a60248201527f4d757374206e6f7420626520616e204552433136352068617368000000000000604482015290519081900360640190fd5b600160a060020a038216158015906103b85750600160a060020a0382163314155b156104ff5760405160200180807f455243313832305f4143434550545f4d4147494300000000000000000000000081525060140190506040516020818303038152906040528051906020012082600160a060020a031663249cb3fa85846040518363ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004018083815260200182600160a060020a0316600160a060020a031681526020019250505060206040518083038186803b15801561047e57600080fd5b505afa158015610492573d6000803e3d6000fd5b505050506040513d60208110156104a857600080fd5b5051146104ff576040805160e560020a62461bcd02815260206004820181905260248201527f446f6573206e6f7420696d706c656d656e742074686520696e74657266616365604482015290519081900360640190fd5b600160a060020a03818116600081815260208181526040808320888452909152808220805473ffffffffffffffffffffffffffffffffffffffff19169487169485179055518692917f93baa6efbd2244243bfee6ce4cfdd1d04fc4c0e9a786abd3a41313bd352db15391a450505050565b600160a060020a03818116600090815260016020526040812054909116151561059a5750806105b7565b50600160a060020a03808216600090815260016020526040902054165b919050565b336105c683610570565b600160a060020a031614610624576040805160e560020a62461bcd02815260206004820152600f60248201527f4e6f7420746865206d616e616765720000000000000000000000000000000000604482015290519081900360640190fd5b81600160a060020a031681600160a060020a0316146106435780610646565b60005b600160a060020a03838116600081815260016020526040808220805473ffffffffffffffffffffffffffffffffffffffff19169585169590951790945592519184169290917f605c2dbf762e5f7d60a546d42e7205dcb1b011ebc62a61736a57c9089d3a43509190a35050565b600082826040516020018083838082843780830192505050925050506040516020818303038152906040528051906020012090505b92915050565b6106f882826107ef565b610703576000610705565b815b600160a060020a03928316600081815260208181526040808320600160e060020a031996909616808452958252808320805473ffffffffffffffffffffffffffffffffffffffff19169590971694909417909555908152600284528181209281529190925220805460ff19166001179055565b600080600160a060020a038416156107905783610792565b335b905061079d8361092a565b156107c357826107ad82826108aa565b6107b85760006107ba565b815b925050506106e8565b600160a060020a0390811660009081526020818152604080832086845290915290205416905092915050565b6000808061081d857f01ffc9a70000000000000000000000000000000000000000000000000000000061094c565b909250905081158061082d575080155b1561083d576000925050506106e8565b61084f85600160e060020a031961094c565b909250905081158061086057508015155b15610870576000925050506106e8565b61087a858561094c565b909250905060018214801561088f5750806001145b1561089f576001925050506106e8565b506000949350505050565b600160a060020a0382166000908152600260209081526040808320600160e060020a03198516845290915281205460ff1615156108f2576108eb83836107ef565b90506106e8565b50600160a060020a03808316600081815260208181526040808320600160e060020a0319871684529091529020549091161492915050565b7bffffffffffffffffffffffffffffffffffffffffffffffffffffffff161590565b6040517f01ffc9a7000000000000000000000000000000000000000000000000000000008082526004820183905260009182919060208160248189617530fa90519096909550935050505056fea165627a7a72305820377f4a2d4301ede9949f163f319021a6e9c687c292a5e2b2c4734c126b524e6c00291ba01820182018201820182018201820182018201820182018201820182018201820a01820182018201820182018201820182018201820182018201820182018201820'
    a[0].transfer(ERC1820_DEPLOYER, ERC1820_ETH_AMOUNT)
    web3.eth.send_raw_transaction(ERC1820_PAYLOAD)
    
    return deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner)


@pytest.fixture(scope="module")
def auto(cleanAUTO):
    auto = cleanAUTO
    # For enabling rewards
    auto.AUTO.transfer(auto.m, INIT_AUTO_REW_POOL, auto.FR_DEPLOYER)
    # For being able to test staking with
    auto.AUTO.transfer(auto.ALICE, MAX_TEST_STAKE, auto.FR_DEPLOYER)
    auto.AUTO.transfer(auto.BOB, MAX_TEST_STAKE, auto.FR_DEPLOYER)
    auto.AUTO.transfer(auto.CHARLIE, MAX_TEST_STAKE, auto.FR_DEPLOYER)

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
    vuln = auto.DEPLOYER.deploy(VulnerableStaker, auto.o.address, auto.AUTO.address)
    vuln.setAUTO(auto.AUTO, auto.FR_DEPLOYER)
    
    return vuln


# Need to have already staked properly in order to test `noFish`
@pytest.fixture(scope="module")
def vulnerableStaked(auto, vulnerableStaker):
    staker = auto.ALICE
    auto.AUTO.authorizeOperator(vulnerableStaker, {'from': staker})
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
        auto.sm,
        auto.o,
        auto.uf,
        auto.ff,
        auto.uff,
        "Autonomy Network",
        "AUTO",
        INIT_AUTO_SUPPLY
    )


# Need to have some 'external' contract whose state needs changing in order
# to use AUTO
@pytest.fixture(scope="module")
def mockTarget(auto, MockTarget, vulnerableRegistry):
    return auto.DEPLOYER.deploy(MockTarget, auto.uf, auto.ff, auto.uff, auto.r, vulnerableRegistry)


# Need to test nonReentrant modifier
@pytest.fixture(scope="module")
def mockReentrancyAttack(auto, MockReentrancyAttack):
    return auto.DEPLOYER.deploy(MockReentrancyAttack, auto.r)


# Need to test gas usage with the exact same rounding profile that Solidity
# uses vs Python
@pytest.fixture(scope="module")
def evmMaths(cleanAUTO, EVMMaths):
    return cleanAUTO.DEPLOYER.deploy(EVMMaths)


# Need to have some requests to test executeHashedReq. Need a request that has ethForCall
# set to 0 and 1 that doesn't, and 1 that pays with AUTO with ethForCall and 1 without
@pytest.fixture(scope="module")
def hashedReqs(auto, mockTarget):
    ethForCall = E_18
    msgValue = int(1.5 * ethForCall)
    reqs = []

    # Set a var on a target without sending ETH with the call, pay upfront
    callData = mockTarget.setX.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, 0, False, False, False, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, False, False, {'from': auto.BOB, 'value': msgValue})

    # Set a var on a target, sending ETH with the call, pay upfront
    callData = mockTarget.setXPay.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, False, False, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, False, False, False, False, {'from': auto.BOB, 'value': msgValue})

    # Set a var on a target, paying with AUTO after execution
    callData = mockTarget.setX.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, True, False, {'from': auto.BOB, 'value': 0})

    # Set a var on a target, sending ETH witht the call, paying with AUTO after execution
    callData = mockTarget.setXPay.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, False, True, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, False, False, True, False, {'from': auto.BOB, 'value': ethForCall})

    # Set an address that is the original users' address on a target, pay with AUTO after execution
    callData = mockTarget.setAddrPayUserVerified.encode_input(auto.BOB)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, True, False, True, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, True, False, True, False, {'from': auto.BOB, 'value': ethForCall})

    # Set a var that is what the gas the execution charges for, sending ETH with the call, pay with AUTO after execution
    callData = mockTarget.setXPayFeeVerified.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, True, True, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, False, True, True, False, {'from': auto.BOB, 'value': ethForCall})

    # Set a var that is the user's address and the gas the execution charges for, pay for execution with ETH sent from the target
    callData = mockTarget.setAddrXPayUserFeeVerifiedSendEth.encode_input(auto.BOB, 5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, True, True, False, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, True, True, False, False, {'from': auto.BOB, 'value': 0})

    # Set a var that is the user's address and the gas the execution charges for, send ETH with call, pay with AUTO 
    callData = mockTarget.setAddrXPayUserFeeVerified.encode_input(auto.BOB, 5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, True, True, True, False))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, True, True, True, False, {'from': auto.BOB, 'value': ethForCall})

    # Set a var on a target, pay in AUTO, and have it be recurring
    callData = mockTarget.setX.encode_input(5)
    reqs.append((auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, True))
    tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, True, True, {'from': auto.BOB, 'value': 0})

    reqHashes = [keccakReq(auto, r) for r in reqs]

    return reqs, reqHashes, msgValue, ethForCall


# With hashReqNoEth, we can't send eth in the call and have to pay via AUTO, so
# only one combination this time
@pytest.fixture(scope="module")
def hashedReqUnveri(auto, mockTarget):
    auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False)
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
    reqEthForCall = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, msgValue, ethForCall, False, False, False, False)
    tx = vulnerableRegistry.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, False, False, False, False, {'from': auto.BOB, 'value': msgValue})

    auto.AUTO.approve(vulnerableRegistry, MAX_TEST_STAKE, auto.FR_BOB)

    reqPayAUTOEthForCall = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, ethForCall, ethForCall, False, False, True, False)
    tx = vulnerableRegistry.newReqPaySpecific(mockTarget, auto.DENICE, callData, ethForCall, False, False, True, False, {'from': auto.BOB, 'value': ethForCall})

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
    req = (auto.BOB.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, True, False)
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