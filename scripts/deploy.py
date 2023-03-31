from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock
from brownie.network import priority_fee
import sys
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.append(os.path.abspath('scripts'))
from addresses import *
sys.path.pop()



if network.show_active() == 'development':
    PUBLISH_SOURCE = False
else:
    priority_fee("1 gwei")
    PUBLISH_SOURCE = True

deployer = accounts.add(os.environ['DEPLOYER_PRIV'])

def main():
    class Context:
        pass

    auto = Context()

    auto.DEPLOYER = deployer
    auto.FR_DEPLOYER = {"from": auto.DEPLOYER}
    print(auto.DEPLOYER)

    auto.po = auto.DEPLOYER.deploy(PriceOracle, INIT_AUTO_PER_ETH_WEI, 200*10**9, publish_source=PUBLISH_SOURCE)
    auto.o = auto.DEPLOYER.deploy(Oracle, auto.po, False, publish_source=PUBLISH_SOURCE)
    auto.sm = auto.DEPLOYER.deploy(StakeManager, auto.o, publish_source=PUBLISH_SOURCE)
    auto.uf = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE)
    auto.ff = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE)
    auto.uff = auto.DEPLOYER.deploy(Forwarder, publish_source=PUBLISH_SOURCE)
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
        publish_source=PUBLISH_SOURCE
    )
    auto.AUTO = AUTO.at(auto.r.getAUTOAddr())
    auto.sm.setAUTO(auto.AUTO, auto.FR_DEPLOYER)
    auto.uf.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.ff.setCaller(auto.r, True, auto.FR_DEPLOYER)
    auto.uff.setCaller(auto.r, True, auto.FR_DEPLOYER)

    # Create timelock for OP owner
    auto.tl = auto.DEPLOYER.deploy(Timelock, auto.DEPLOYER, int(DAY/2), publish_source=PUBLISH_SOURCE)
    auto.po.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.o.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uf.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.ff.transferOwnership(auto.tl, auto.FR_DEPLOYER)
    auto.uff.transferOwnership(auto.tl, auto.FR_DEPLOYER)

    print(f'PriceOracle deployed at: {auto.po.address}')
    print(f'Oracle deployed at: {auto.o.address}')
    print(f'StakeManager deployed at: {auto.sm.address}')
    print(f'User Forwarder deployed at: {auto.uf.address}')
    print(f'Fee Forwarder deployed at: {auto.ff.address}')
    print(f'User Fee Forwarder deployed at: {auto.uff.address}')
    print(f'Registry deployed at: {auto.r.address}')
    print(f'Timelock deployed at: {auto.tl.address}')
