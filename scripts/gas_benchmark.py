from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, MockTarget
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
from conftest import deploy_initial_AUTO_contracts, mockTarget
sys.path.pop()


def main():
    auto = deploy_initial_AUTO_contracts(AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner)
    mockTarget = auto.DEPLOYER.deploy(MockTarget, auto.vf, ADDR_0)

    callData = mockTarget.setX.encode_input(5)
    
    # It'll cost extra the first time using the array
    tx = auto.r.newHashedReq(mockTarget, auto.DENICE, callData, 0, False, True, "", "", auto.FR_BOB)
    print(f'newHashedReq = {tx.gas_used}')
    
    tx = auto.r.newHashedReq(mockTarget, auto.DENICE, callData, 0, False, True, "", "", auto.FR_BOB)
    print(f'newHashedReq = {tx.gas_used}')

    tx = auto.r.newHashedReqEvent(mockTarget, auto.DENICE, callData, 0, False, True, auto.FR_BOB)
    print(f'newHashedReqEvent = {tx.gas_used}')
    print(tx.events)

    tx = auto.r.newHashedReqEvent2(mockTarget, auto.DENICE, callData, 0, False, True, auto.FR_BOB)
    print(f'newHashedReqEvent2 = {tx.gas_used}')

    # It'll cost extra the first time using the array
    tx = auto.r.newHashedReqUnveri('0000000000000000000000000000000000000000000000000000000000000001')
    print(f'newHashedReqUnveri = {tx.gas_used}')

    tx = auto.r.newHashedReqUnveri('0000000000000000000000000000000000000000000000000000000000000001')
    print(f'newHashedReqUnveri = {tx.gas_used}')
