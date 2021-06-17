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
# AUTO_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
# PRICE_ORACLE_ADDR = '0x5d30C97498F1F81e4A57386Ebea7aC8E3892fb5d'
# ORACLE_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'
# SM_ADDR = '0x1B251B968b5A2FdE5E126BFF1DA3739ca49e1CA0'
# FORWARDER_ADDR = '0xD1DEdEb7871F1dd55cA26746650378723c26Be5d'
REGISTRY_ADDR = '0x34B8a833d39041119b738200975460F47BbA5bbc'
# MINER_ADDR = '0xA22de268AE155ce9EaC33124890d91294d694497'

def main():
    r = Registry.at(REGISTRY_ADDR)
    ethForCall = 5 * 10**16
    r.newReq(DEPLOYER, ADDR_0, '', ethForCall, False, False, {'value': ethForCall + 10**16, 'from': DEPLOYER})