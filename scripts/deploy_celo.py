from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock
import sys
import yaml
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
PUBLISH_SOURCE = False

def main():
    class Context:
        pass

    auto = Context()

    auto.DEPLOYER = accounts.add(cfg['AUTONOMY_PRIV'])
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}
    print(auto.DEPLOYER)

    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po, False, publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, publish_source=PUBLISH_SOURCE, gas_limit=1e8)
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
        INIT_REFERAL_REWARD,
        publish_source=PUBLISH_SOURCE, gas_limit=1e7
    )

    # Create timelock for OP owner
    auto.tl = auto.DEPLOYER.deploy(Timelock, '0x08a998AbC0C91DBe949C2D93de3998Dae4235852', int(DAY/2), publish_source=PUBLISH_SOURCE, gas_limit=1e7)
    auto.po.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.o.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uf.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.ff.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uff.transferOwnership(auto.tl, auto.FR_DEPLOYER)
