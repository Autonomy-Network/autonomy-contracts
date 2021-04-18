from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(asc):
    assert asc.po.getASCPerUSD() == INIT_ASC_PER_USD
    assert asc.po.getETHPerUSD() == INIT_ETH_PER_USD
    assert asc.po.owner() == asc.DEPLOYER


@given(newRate=strategy('uint'))
def test_updateASCPerUSD(asc, newRate):
    asc.po.updateASCPerUSD(newRate, asc.FR_DEPLOYER)
    
    assert asc.po.getASCPerUSD() == newRate
    assert asc.po.getETHPerUSD() == INIT_ETH_PER_USD
    assert asc.po.owner() == asc.DEPLOYER
    assert asc.o.getASCPerUSD() == newRate
    assert asc.o.getETHPerUSD() == INIT_ETH_PER_USD


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateASCPerUSD_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.po.updateASCPerUSD(newRate, {'from': sender})


@given(newRate=strategy('uint'))
def test_updateETHPerUSD(asc, newRate):
    asc.po.updateETHPerUSD(newRate, asc.FR_DEPLOYER)
    
    assert asc.po.getASCPerUSD() == INIT_ASC_PER_USD
    assert asc.po.getETHPerUSD() == newRate
    assert asc.po.owner() == asc.DEPLOYER
    assert asc.o.getASCPerUSD() == INIT_ASC_PER_USD
    assert asc.o.getETHPerUSD() == newRate


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateETHPerUSD_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.po.updateETHPerUSD(newRate, {'from': sender})