from brownie import accounts, EthSender
import os


AUTONOMY_SEED = os.environ['AUTONOMY_SEED']
auto_accs = accounts.from_mnemonic(AUTONOMY_SEED, count=10)
DEPLOYER = auto_accs[4]


def main():
    DEPLOYER.deploy(EthSender, publish_source=True)