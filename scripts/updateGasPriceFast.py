from brownie import accounts, chain, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner, Timelock
import sys
import os
sys.path.append(os.path.abspath('tests'))
from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)

# BSC mainnet
PO_ADDR = '0x957Fa92cAc1AD4447B6AEc163af57e7E36537c91'
TL_ADDR = '0x9Ce05ad236Ad29B9EF6597633201631c097c3f10'
# ETH Ropsten
# PO_ADDR = '0x70597A4cdf2454878F542991e1BB0a550A646879'
# TL_ADDR = '0xCCe3761011919a2C63624A4B9247E4e6336F637F'

def main():
    DEPLOYER = auto_accs[4]
    FR_DEPLOYER = {"from": DEPLOYER}

    po = PriceOracle.at(PO_ADDR)
    tl = Timelock.at(TL_ADDR)

    callData = po.updateGasPriceFast.encode_input(3*10**9)
    delay = 2*DAY
    args = (po, 0, "", callData, 1632503987)
    # tl.queueTransaction(*args, FR_DEPLOYER)

    tl.executeTransaction(*args, FR_DEPLOYER)