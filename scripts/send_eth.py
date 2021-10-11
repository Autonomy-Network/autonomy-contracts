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

# Ropsten:
REGISTRY_ADDR = '0x3C901dc595105934D61DB70C2170D3a6834Cb8B7'

def main():
    r = Registry.at(REGISTRY_ADDR)
    ethForCall = 5 * 10**16
    r.newReqPaySpecific(DEPLOYER, ADDR_0, '', ethForCall, False, False, False, False, {'value': ethForCall + 10**16, 'from': DEPLOYER})