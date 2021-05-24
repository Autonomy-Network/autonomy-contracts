from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(asc):
    assert asc.po.getAUTOPerETH() == INIT_AUTO_PER_ETH
    assert asc.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert asc.po.owner() == asc.DEPLOYER


@given(newRate=strategy('uint'))
def test_updateAUTOPerETH(asc, newRate):
    asc.po.updateAUTOPerETH(newRate, asc.FR_DEPLOYER)
    
    assert asc.po.getAUTOPerETH() == newRate
    assert asc.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert asc.po.owner() == asc.DEPLOYER
    assert asc.o.getAUTOPerETH() == newRate
    assert asc.o.getGasPriceFast() == INIT_GAS_PRICE_FAST


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateAUTOPerETH_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.po.updateAUTOPerETH(newRate, {'from': sender})


@given(newRate=strategy('uint'))
def test_updateGasPriceFast(asc, newRate):
    asc.po.updateGasPriceFast(newRate, asc.FR_DEPLOYER)
    
    assert asc.po.getAUTOPerETH() == INIT_AUTO_PER_ETH
    assert asc.po.getGasPriceFast() == newRate
    assert asc.po.owner() == asc.DEPLOYER
    assert asc.o.getAUTOPerETH() == INIT_AUTO_PER_ETH
    assert asc.o.getGasPriceFast() == newRate


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateGasPriceFast_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.po.updateGasPriceFast(newRate, {'from': sender})