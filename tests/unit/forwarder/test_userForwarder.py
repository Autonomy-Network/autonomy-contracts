from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy


def test_initial_state(auto):
    checkAreCallers(auto.uf, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m], [auto.r])
    assert auto.uf.owner() == auto.DEPLOYER


@given(newCaller=strategy('address'), b=strategy('bool'))
def test_setCaller(a, auto, newCaller, b):
    auto.uf.setCaller(newCaller, b, auto.FR_DEPLOYER)
    if str(newCaller) == str(auto.r):
        callers = [auto.r] if b else []
    else:
        callers = [auto.r, newCaller] if b else [auto.r]

    checkAreCallers(auto.uf, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m], callers)


def test_setReg_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.DEPLOYER:
            with reverts(REV_MSG_OWNER):
                auto.uf.setCaller(ADDR_0, True, {'from': sender})


def test_forward_rev_not_reg(a, auto):
    for sender in list(a) + auto.all:
        if sender.address != auto.r.address:
            with reverts(REV_MSG_NOT_REG):
                auto.uf.forward(ADDR_0, '', {'from': sender})