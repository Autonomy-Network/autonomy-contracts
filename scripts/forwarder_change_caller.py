from brownie import accounts, AUTO, PriceOracle, Oracle, StakeManager, Registry, Forwarder, Miner
import sys
import os
sys.path.append(os.path.abspath('tests'))

from consts import *
sys.path.pop()


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
DEPLOYER = auto_accs[4]

# Ropsten:
# AUTO_ADDR = '0xE3e761127cBD037E18186698a2733d1e71623ebE'
# PRICE_ORACLE_ADDR = '0xEBECAe5f1249101c818FC4681adA52d097Aa3d3b'
# ORACLE_ADDR = '0x3d0c9dC70c12eC0A6f5422c86E3cB4B2Bb6ABfAA'
# SM_ADDR = '0x439468ED7a1ACBf5A73E5067da1B35cf8bF82Cec'
FORWARDER_ADDR = '0xD1DEdEb7871F1dd55cA26746650378723c26Be5d'
REGISTRY_ADDR = '0xB82Ae7779aB1742734fCE32A4b7fDBCf020F2667'
# MINER_ADDR = '0x9d7c55d2f2dAA1d269BFc78d375D883750A6D50E'

def main():
    f = Forwarder.at(FORWARDER_ADDR)
    f.setCaller(REGISTRY_ADDR, True, {'from': DEPLOYER})