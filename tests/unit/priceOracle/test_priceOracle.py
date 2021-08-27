from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(auto):
    assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.po.owner() == auto.DEPLOYER


@given(newRate=strategy('uint'))
def test_updateAUTOPerETH(auto, newRate):
    auto.po.updateAUTOPerETH(newRate, auto.FR_DEPLOYER)
    
    assert auto.po.getAUTOPerETH() == newRate
    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.po.owner() == auto.DEPLOYER
    assert auto.o.getAUTOPerETH() == newRate
    assert auto.o.getGasPriceFast() == INIT_GAS_PRICE_FAST


def test_updateAUTOPerETH_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.DEPLOYER:
            with reverts(REV_MSG_OWNER):
                auto.po.updateAUTOPerETH(3, {'from': sender})


@given(newRate=strategy('uint'))
def test_updateGasPriceFast(auto, newRate):
    auto.po.updateGasPriceFast(newRate, auto.FR_DEPLOYER)
    
    assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.po.getGasPriceFast() == newRate
    assert auto.po.owner() == auto.DEPLOYER
    assert auto.o.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.o.getGasPriceFast() == newRate


def test_updateGasPriceFast_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.DEPLOYER:
            with reverts(REV_MSG_OWNER):
                auto.po.updateGasPriceFast(3, {'from': sender})