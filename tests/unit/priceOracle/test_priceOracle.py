from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(asc):
    assert asc.po.getASCPerETH() == INIT_ETH_TO_ASCOIN_RATE
    assert asc.po.owner() == asc.DEPLOYER


@given(newRate=strategy('uint'))
def test_updateASCPerETH(asc, newRate):
    asc.po.updateASCPerETH(newRate, asc.FR_DEPLOYER)
    
    assert asc.po.getASCPerETH() == newRate
    assert asc.po.owner() == asc.DEPLOYER
    assert asc.o.getASCPerETH() == newRate


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateASCPerETH_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.po.updateASCPerETH(newRate, {'from': sender})