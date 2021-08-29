from consts import *
from brownie.test import given, strategy
from brownie import reverts


def test_setAUTO(a, auto, StakeManager):
    for addr in a:
        sm = auto.DEPLOYER.deploy(StakeManager, auto.o)
        
        assert sm.getAUTOAddr() == ADDR_0

        sm.setAUTO(addr, auto.FR_DEPLOYER)

        assert sm.getAUTOAddr() == str(addr)


@given(
    initAUTO=strategy('address'),
    newAUTO=strategy('address'),
    initSender=strategy('address'),
    sender=strategy('address')
)
def test_setAUTO_rev_set(a, auto, StakeManager, initAUTO, newAUTO, initSender, sender):
    sm = auto.DEPLOYER.deploy(StakeManager, auto.o)
    
    assert sm.getAUTOAddr() == ADDR_0
    
    sm.setAUTO(initAUTO, {'from': initSender})
    
    assert sm.getAUTOAddr() == str(initAUTO)

    for addr in a:
        with reverts(REV_MSG_AUTO_SET):
            sm.setAUTO(newAUTO, {'from': sender})