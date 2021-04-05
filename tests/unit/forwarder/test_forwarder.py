from consts import *
from brownie import reverts
from brownie.test import given, strategy


# Should only really need to test just 1 of vf/uvf, but... something something paranoia?
def test_initial_state(asc):
    assert asc.vf.getReg() == asc.r.address
    assert asc.uvf.getReg() == asc.r.address
    assert asc.vf.owner() == asc.DEPLOYER
    assert asc.uvf.owner() == asc.DEPLOYER


@given(addr=strategy('address'))
def test_setReg(asc, addr):
    asc.vf.setReg(addr, asc.FR_DEPLOYER)
    assert asc.vf.getReg() == addr
    asc.uvf.setReg(addr, asc.FR_DEPLOYER)
    assert asc.uvf.getReg() == addr


@given(
    addr=strategy('address'),
    sender=strategy('address')
)
def test_setReg_rev_owner(asc, addr, sender):
    if sender != asc.DEPLOYER:
        with reverts(REV_MSG_OWNER):
            asc.vf.setReg(addr, {'from': sender})
        with reverts(REV_MSG_OWNER):
            asc.uvf.setReg(addr, {'from': sender})
