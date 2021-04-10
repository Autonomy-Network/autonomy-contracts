from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_initial_state(asc):
    assert asc.o.getASCPerETH() == INIT_ETH_TO_ASCOIN_RATE
    assert asc.o.owner() == asc.DEPLOYER


def test_getRandNum(asc):
    for i in range(1000):
        chain.mine(1)
        assert getRandNum(i) == asc.o.getRandNum(i)


@given(newRate=strategy('uint'))
def test_updateASCPerETH(asc, newRate):
    asc.o.updateASCPerETH(newRate, asc.FR_DEPLOYER)
    assert asc.o.getASCPerETH() == newRate
    assert asc.o.owner() == asc.DEPLOYER


@given(
    newRate=strategy('uint'),
    sender=strategy('address')
)
def test_updateASCPerETH_rev_owner(asc, newRate, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.o.updateASCPerETH(newRate, {'from': sender})