from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy


def test_constructor(auto):
    assert auto.sm.getOracle() == auto.o.address
    assert auto.sm.getAUTOAddr() == auto.AUTO.address
    assert auto.sm.getTotalStaked() == 0
    assert auto.sm.getStake(auto.DEPLOYER) == 0
    assert len(auto.sm.getStakes()) == 0
    assert auto.sm.getCurEpoch() == getEpoch(bn())


def test_rev_send_non_AUTO_token(auto, AUTO):
    token = auto.DEPLOYER.deploy(AUTO, "Shitcoin", "SHIT", [], auto.DEPLOYER, 1000)
    with reverts(REV_MSG_NON_AUTO_TOKEN):
        token.transfer(auto.sm, 3, auto.FR_DEPLOYER)


def test_transfer_rev_sent_by_mistake(auto):
    with reverts(REV_MSG_MISTAKE):
        auto.AUTO.transfer(auto.sm, 3, auto.FR_DEPLOYER)


@given(b=strategy('bytes'))
def test_send_rev_sent_by_mistake(auto, b):
    # 7374616b696e67 is 'staking' in hex
    if b.hex() != "7374616b696e67":
        with reverts(REV_MSG_MISTAKE):
            auto.AUTO.send(auto.sm, 3, b, auto.FR_DEPLOYER)