from brownie import accounts, chain, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock
import time
import sys
import yaml
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

# # BSC mainnet
# PO_ADDR = '0x957Fa92cAc1AD4447B6AEc163af57e7E36537c91'
# TL_ADDR = '0x9Ce05ad236Ad29B9EF6597633201631c097c3f10'
# ETH Ropsten
# PO_ADDR = '0x70597A4cdf2454878F542991e1BB0a550A646879'
# TL_ADDR = '0xCCe3761011919a2C63624A4B9247E4e6336F637F'
# # AVAX testnet
# PO_ADDR = '0xCCa7a3b74919AEC8387b99F21F92221ea35Cc016'
# TL_ADDR = '0x31510CB811E5ea0F484b84a04573Ba2d288d4426'
# AVAX mainnet
PO_ADDR = '0x9118dbc12dc5979daBCe6782739b020b8908a6CB'
TL_ADDR = '0xA9E74167a120B139eBdf0858401FFd85b64E4810'


def main():
    DEPLOYER = accounts.add(cfg['AUTONOMY_PRIV'])
    FR_DEPLOYER = {"from": DEPLOYER}

    po = PriceOracle.at(PO_ADDR)
    tl = Timelock.at(TL_ADDR)

    callData = po.updateGasPriceFast.encode_input(25*10**9)
    exec_time = time.time() + (12 * HOUR) + 100
    print(exec_time)
    # 1642555645
    args = (po, 0, "", callData, 1642555645)
    # tl.queueTransaction(*args, FR_DEPLOYER)

    tl.executeTransaction(*args, FR_DEPLOYER)
