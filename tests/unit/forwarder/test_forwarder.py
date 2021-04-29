from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy


def test_initial_state(asc):
    checkAreCallers(asc, a[:] + [asc.ASC, asc.po, asc.o, asc.sm, asc.vf, asc.r, asc.m], [asc.r])
    assert asc.vf.owner() == asc.DEPLOYER


@given(newCaller=strategy('address'), b=strategy('bool'))
def test_setCaller(a, asc, newCaller, b):
    asc.vf.setCaller(newCaller, b, asc.FR_DEPLOYER)
    callers = [asc.r, newCaller] if b else [asc.r]

    checkAreCallers(asc, a[:] + [asc.ASC, asc.po, asc.o, asc.sm, asc.vf, asc.r, asc.m], callers)


@given(
    addr=strategy('address'),
    b=strategy('bool'),
    sender=strategy('address')
)
def test_setReg_rev_owner(asc, addr, b, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.vf.setCaller(addr, b, {'from': sender})


@given(
    target=strategy('address'),
    callData=strategy('bytes'),
    sender=strategy('address')
)
def test_forward_rev_not_reg(asc, target, callData, sender):
    with reverts(REV_MSG_NOT_REG):
        asc.vf.forward(target, callData, {'from': sender})