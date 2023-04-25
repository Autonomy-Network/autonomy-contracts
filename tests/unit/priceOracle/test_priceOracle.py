from consts import *
from brownie import chain, reverts, web3
from brownie.test import given, strategy
from utils import *


def test_constructor(auto):
    assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.po.owner() == auto.tl


@given(newRate=strategy('uint'))
def test_updateAUTOPerETH(auto, newRate):
    callData = auto.po.updateAUTOPerETH.encode_input(newRate)
    delay = 2*DAY
    args = (auto.po, 0, "", callData, chain.time() + delay + 60)
    auto.tl.queueTransaction(*args)
    chain.sleep(delay + 120)
    auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
    assert auto.po.getAUTOPerETH() == newRate
    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.po.owner() == auto.tl
    assert auto.o.getAUTOPerETH() == newRate
    assert auto.o.getGasPriceFast() == INIT_GAS_PRICE_FAST


def test_updateAUTOPerETH_rev_timelock(auto):
    newRate = 17
    callData = auto.po.updateAUTOPerETH.encode_input(newRate)
    delay = 2*DAY
    args = (auto.po, 0, "", callData, chain.time() + delay + 60)
    auto.tl.queueTransaction(*args)
    chain.sleep(delay + 120)
    auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
    assert auto.po.getAUTOPerETH() == newRate
    assert auto.po.getGasPriceFast() == INIT_GAS_PRICE_FAST
    assert auto.po.owner() == auto.tl
    assert auto.o.getAUTOPerETH() == newRate
    assert auto.o.getGasPriceFast() == INIT_GAS_PRICE_FAST


def test_updateAUTOPerETH_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.tl:
            with reverts(REV_MSG_OWNER):
                auto.po.updateAUTOPerETH(3, {'from': sender})


# @given(newRate=strategy('uint'))
# def test_updateGasPriceFast(auto, newRate):
#     callData = auto.po.updateGasPriceFast.encode_input(newRate)
#     delay = 2*DAY
#     args = (auto.po, 0, "", callData, chain.time() + delay + 60)
#     auto.tl.queueTransaction(*args)
#     chain.sleep(delay + 120)
#     auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
#     assert auto.po.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
#     assert auto.po.getGasPriceFast() == newRate
#     assert auto.po.owner() == auto.tl
#     assert auto.o.getAUTOPerETH() == INIT_AUTO_PER_ETH_WEI
#     assert auto.o.getGasPriceFast() == newRate


# def test_updateGasPriceFast_rev_owner(a, auto):
#     for sender in list(a) + auto.all:
#         if sender != auto.tl:
#             with reverts(REV_MSG_OWNER):
#                 auto.po.updateGasPriceFast(3, {'from': sender})