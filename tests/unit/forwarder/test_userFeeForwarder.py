from consts import *
from utils import *
from brownie import reverts, chain
from brownie.test import given, strategy


def test_initial_state(auto):
    checkAreCallers(auto.uff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m, auto.tl], [auto.r])
    assert auto.uff.owner() == auto.tl


@given(newCaller=strategy('address'), b=strategy('bool'))
def test_setCaller(a, auto, newCaller, b):
    callData = auto.uff.setCaller.encode_input(newCaller, b)
    delay = 2*DAY
    args = (auto.uff, 0, "", callData, chain.time() + delay + 60)
    auto.tl.queueTransaction(*args)
    chain.sleep(delay + 120)
    auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)
    
    if str(newCaller) == str(auto.r):
        callers = [auto.r] if b else []
    else:
        callers = [auto.r, newCaller] if b else [auto.r]

    checkAreCallers(auto.uff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m, auto.tl], callers)


def test_setReg_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.tl:
            with reverts(REV_MSG_OWNER):
                auto.uff.setCaller(ADDR_0, True, {'from': sender})


def test_forward_rev_not_reg(a, auto):
    for sender in list(a) + auto.all:
        if sender.address != auto.r.address:
            with reverts(REV_MSG_NOT_REG):
                auto.uff.forward(ADDR_0, '', {'from': sender})