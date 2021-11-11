from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
DEPLOYER = auto_accs[4]
print(DEPLOYER)
FR_DEPLOYER = {"from": DEPLOYER}

REGISTRY_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'

def main():
    r = Registry.at(REGISTRY_ADDR)
    ethForCall = 5 * 10**16
    r.newReq(DEPLOYER, ADDR_0, '', ethForCall, False, False, False, {'value': ethForCall + 10**16, 'from': DEPLOYER})