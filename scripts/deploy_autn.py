from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock, TProxy, TProxyAdmin
import sys
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
print(auto_accs)

def main():
    deployer = auto_accs[9]
    # print(deployer)
    # print(auto_accs[10])

    return AUTO.deploy("Autonomy Network", "AUTN", [], deployer, INIT_AUTO_SUPPLY, {'from': deployer}, publish_source=True)