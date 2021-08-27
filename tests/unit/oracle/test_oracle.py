from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(auto):
    assert auto.o.getPriceOracle() == auto.po
    assert auto.o.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.o.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.o.owner() == auto.DEPLOYER


# def test_getRandNum(auto):
#     for i in range(1000):
#         chain.mine(1)
#         assert getRandNum(i) == auto.o.getRandNum(i)


# Test with a new price oracle so we can test that getAUTOPerETH
# properly reads the new price
def test_setPriceOracle(auto, PriceOracle):
    newRate = 17
    newGasPriceFast = 3 * 10**9
    newPriceOracle = auto.DEPLOYER.deploy(PriceOracle, newRate, newGasPriceFast)

    auto.o.setPriceOracle(newPriceOracle, auto.FR_DEPLOYER)
    
    assert auto.o.getAUTOPerETH() == newRate
    assert auto.o.getGasPriceFast() == newGasPriceFast
    assert auto.o.owner() == auto.DEPLOYER


@given(newPriceOracle=strategy('address'))
def test_setPriceOracle_rand(auto, newPriceOracle):
    auto.o.setPriceOracle(newPriceOracle, auto.FR_DEPLOYER)
    
    assert auto.o.getPriceOracle() == newPriceOracle
    assert auto.o.owner() == auto.DEPLOYER


def test_setPriceOracle_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.DEPLOYER:
            with reverts(REV_MSG_OWNER):
                auto.o.setPriceOracle(ADDR_0, {'from': sender})


@given(newDefaultPayIsAUTO=strategy('bool'))
def test_setDefaultPayIsAUTO_rand(auto, newDefaultPayIsAUTO):
    auto.o.setDefaultPayIsAUTO(newDefaultPayIsAUTO, auto.FR_DEPLOYER)
    
    assert auto.o.getPriceOracle() == auto.po
    assert auto.o.defaultPayIsAUTO() == newDefaultPayIsAUTO
    assert auto.o.owner() == auto.DEPLOYER


def test_setDefaultPayIsAUTO_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.DEPLOYER:
            with reverts(REV_MSG_OWNER):
                auto.o.setDefaultPayIsAUTO(True, {'from': sender})