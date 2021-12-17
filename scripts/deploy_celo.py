from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock
import sys
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
PUBLISH_SOURCE = False

def main():
    class Context:
        pass

    auto = Context()

    auto.DEPLOYER = auto_accs[4]
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}
    print(auto.DEPLOYER)

    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po, False, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.uf = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.ff = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.uff = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.r = auto.DEPLOYER.deploy(
        Registry,
        auto.sm,
        auto.o,
        auto.uf,
        auto.ff,
        auto.uff,
        "Autonomy Network",
        "AUTO",
        INIT_AUTO_SUPPLY,
        publish_source=PUBLISH_SOURCE, gas_limit=1e7
    )
    auto.sm.setAUTO(ADDR_0, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.uf.setCaller(auto.r, True, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.ff.setCaller(auto.r, True, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.uff.setCaller(auto.r, True, {'gas_limit': 1e7, 'from': auto.DEPLOYER})

    # Create timelock for OP owner
    auto.tl = auto.DEPLOYER.deploy(Timelock, auto.DEPLOYER, int(DAY/2), publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.po.transferOwnership(auto.tl, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.o.transferOwnership(auto.tl, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.uf.transferOwnership(auto.tl, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.ff.transferOwnership(auto.tl, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
    auto.uff.transferOwnership(auto.tl, {'gas_limit': 1e7, 'from': auto.DEPLOYER})
