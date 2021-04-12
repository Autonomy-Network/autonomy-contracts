from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(asc):
    assert asc.o.getPriceOracle() == asc.po
    assert asc.o.getASCPerETH() == INIT_ETH_TO_ASCOIN_RATE
    assert asc.o.owner() == asc.DEPLOYER


def test_getRandNum(asc):
    for i in range(1000):
        chain.mine(1)
        assert getRandNum(i) == asc.o.getRandNum(i)


# Test with a new price oracle so we can test that getASCPerETH
# properly reads the new price
def test_setPriceOracle(asc, PriceOracle):
    newRate = 15
    newPriceOracle = asc.DEPLOYER.deploy(PriceOracle, newRate)

    asc.o.setPriceOracle(newPriceOracle, asc.FR_DEPLOYER)
    
    assert asc.o.getPriceOracle() == newPriceOracle
    assert asc.o.getASCPerETH() == newRate
    assert asc.o.owner() == asc.DEPLOYER


@given(newPriceOracle=strategy('address'))
def test_setPriceOracle_rand(asc, newPriceOracle):
    asc.o.setPriceOracle(newPriceOracle, asc.FR_DEPLOYER)
    
    assert asc.o.getPriceOracle() == newPriceOracle
    assert asc.o.owner() == asc.DEPLOYER


@given(
    newPriceOracle=strategy('address'),
    sender=strategy('address')
)
def test_setPriceOracle_rev_owner(asc, newPriceOracle, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.o.setPriceOracle(newPriceOracle, {'from': sender})