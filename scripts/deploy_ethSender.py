from brownie import accounts, EthSender
import os
import yaml


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
DEPLOYER = accounts.add(cfg['AUTONOMY_PRIV'])

def main():
    DEPLOYER.deploy(EthSender, publish_source=True)
