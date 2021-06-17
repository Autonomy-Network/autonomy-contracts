from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)

# Ropsten:
# AUTO_ADDR = '0xF2f9793f55c9DAA0b9ba784BC558D90e2035ba86'
# PRICE_ORACLE_ADDR = '0x5d30C97498F1F81e4A57386Ebea7aC8E3892fb5d'
# ORACLE_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'
# SM_ADDR = '0x1B251B968b5A2FdE5E126BFF1DA3739ca49e1CA0'
# FORWARDER_ADDR = '0xD1DEdEb7871F1dd55cA26746650378723c26Be5d'
# REGISTRY_ADDR = '0xD99FbAB1577A4fc6c837D44Ba56166d98bBbA497'
# MINER_ADDR = '0xA22de268AE155ce9EaC33124890d91294d694497'

def main():
    class Context:
        pass

    auto = Context()

    auto.DEPLOYER = auto_accs[4]
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}

    auto.AUTO = auto.DEPLOYER.deploy(AUTO, "Autonomy Network", "AUTO")
    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, auto.AUTO)
    auto.vf = auto.DEPLOYER.deploy(Forwarder)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.AUTO,
        auto.sm,
        auto.o,
        auto.vf
    )
    auto.vf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.m = auto.DEPLOYER.deploy(
        Miner,
        auto.AUTO,
        auto.r,
        INIT_REQUESTER_REWARD,
        INIT_EXECUTOR_REWARD,
        INIT_REFERAL_REWARD
    )