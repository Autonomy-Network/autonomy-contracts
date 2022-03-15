from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner
import sys
import yaml
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
DEPLOYER = accounts.add(cfg['AUTONOMY_PRIV'])
print(DEPLOYER)
FR_DEPLOYER = {"from": DEPLOYER}

REGISTRY_ADDR = '0x2d2C856115911C0D14B9DBfe0FEaB1baBE358D77'

def main():
    r = Registry.at(REGISTRY_ADDR)
    ethForCall = 5 * 10**16
    r.newReq(DEPLOYER, ADDR_0, '', ethForCall, False, False, False, {'value': ethForCall + 10**16, 'from': DEPLOYER})
