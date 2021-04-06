from consts import *
from brownie import reverts
from brownie.test import given, strategy


def test_initial_state(asc):
    assert asc.vf.getReg() == asc.r.address
    assert asc.vf.owner() == asc.DEPLOYER


@given(addr=strategy('address'))
def test_setReg(asc, addr):
    asc.vf.setReg(addr, asc.FR_DEPLOYER)
    assert asc.vf.getReg() == addr


@given(
    addr=strategy('address'),
    sender=strategy('address')
)
def test_setReg_rev_owner(asc, addr, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.vf.setReg(addr, {'from': sender})


@given(
    target=strategy('address'),
    callData=strategy('bytes'),
    sender=strategy('address')
)
def test_forward_rev_not_reg(asc, target, callData, sender):
    with reverts(REV_MSG_NOT_REG):
        asc.vf.forward(target, callData, {'from': sender})