from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy


def test_initial_state(auto):
    checkAreCallers(auto.ff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m], [auto.r])
    assert auto.ff.owner() == auto.DEPLOYER


@given(newCaller=strategy('address'), b=strategy('bool'))
def test_setCaller(a, auto, newCaller, b):
    auto.ff.setCaller(newCaller, b, auto.FR_DEPLOYER)
    callers = [auto.r, newCaller] if b else [auto.r]

    checkAreCallers(auto.ff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m], callers)


@given(
    addr=strategy('address'),
    b=strategy('bool'),
    sender=strategy('address')
)
def test_setReg_rev_owner(auto, addr, b, sender):
    if sender != auto.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            auto.ff.setCaller(addr, b, {'from': sender})


@given(
    target=strategy('address'),
    callData=strategy('bytes'),
    sender=strategy('address')
)
def test_forward_rev_not_reg(auto, target, callData, sender):
    with reverts(REV_MSG_NOT_REG):
        auto.ff.forward(target, callData, {'from': sender})