from consts import *
from utils import *
from brownie import reverts, chain
from brownie.test import given, strategy


def test_initial_state(auto):
    checkAreCallers(auto.ff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m, auto.tl], [auto.r])
    assert auto.ff.owner() == auto.tl


@given(newCaller=strategy('address'), b=strategy('bool'))
def test_setCaller(a, auto, newCaller, b):
    callData = auto.ff.setCaller.encode_input(newCaller, b)
    delay = 2*DAY
    args = (auto.ff, 0, "", callData, chain.time() + delay + 60)
    auto.tl.queueTransaction(*args)
    chain.sleep(delay + 120)
    auto.tl.executeTransaction(*args, auto.FR_DEPLOYER)

    callers = [auto.r, newCaller] if b else [auto.r]

    checkAreCallers(auto.ff, a[:] + [auto.AUTO, auto.po, auto.o, auto.sm, auto.uf, auto.ff, auto.uff, auto.r, auto.m, auto.tl], callers)


def test_setReg_rev_owner(a, auto):
    for sender in list(a) + auto.all:
        if sender != auto.tl:
            with reverts(REV_MSG_OWNER):
                auto.ff.setCaller(ADDR_0, True, {'from': sender})


def test_forward_rev_not_reg(a, auto):
    for sender in list(a) + auto.all:
        if sender.address != auto.r.address:
            with reverts(REV_MSG_NOT_REG):
                auto.ff.forward(ADDR_0, '', {'from': sender})