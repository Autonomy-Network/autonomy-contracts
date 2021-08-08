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


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateAUTOPerETH_rev_owner(auto, newRate, sender):
    if sender != auto.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            auto.po.updateAUTOPerETH(newRate, {'from': sender})


@given(newRate=strategy('uint'))
def test_updateGasPriceFast(auto, newRate):
    auto.po.updateGasPriceFast(newRate, auto.FR_DEPLOYER)
    
    assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.po.getGasPriceFast() == newRate
    assert auto.po.owner() == auto.DEPLOYER
    assert auto.o.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.o.getGasPriceFast() == newRate


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateGasPriceFast_rev_owner(auto, newRate, sender):
    if sender != auto.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            auto.po.updateGasPriceFast(newRate, {'from': sender})