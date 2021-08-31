from consts import *
from utils import *
from brownie import chain, reverts, web3, convert
from brownie.test import given, strategy
from hashlib import sha256
import ipfshttpclient
import base58 as b58


@given(
    user=strategy('address'),
    target=strategy('address'),
    referer=strategy('address'),
    callData=strategy('bytes'),
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
    verifyUser=strategy('bool'),
    insertFeeAmount=strategy('bool'),
    payWithAUTO=strategy('bool'),
    isAlive=strategy('bool')
)
def test_newReqPaySpecific(auto, mockTarget, user, target, referer, callData, msgValue, ethForCall, verifyUser, insertFeeAmount, payWithAUTO, isAlive):
    if user != target and user != referer:
        callData = bytesToHex(callData)
        # assert user.balance() == INIT_ETH_BAL
        userETHStartBal = user.balance()
        # assert referer.balance() == INIT_ETH_BAL
        refererETHStartBal = referer.balance()
        # assert target.balance() == 0
        targetETHStartBal = target.balance()
        assert auto.r.balance() == 0

        # assert auto.AUTO.balanceOf(user) == MAX_TEST_STAKE
        userAUTOStartBal = auto.AUTO.balanceOf(user)
        # assert auto.AUTO.balanceOf(referer) == 0
        refererAUTOStartBal = auto.AUTO.balanceOf(referer)
        # assert auto.AUTO.balanceOf(target) == 0
        targetAUTOStartBal = auto.AUTO.balanceOf(target)
        assert auto.AUTO.balanceOf(auto.r) == 0

        if payWithAUTO:
            msgValue = ethForCall
        else:
            msgValue = ethForCall if msgValue < ethForCall else msgValue

        req = (user, target, referer, callData, msgValue, ethForCall, verifyUser, insertFeeAmount, payWithAUTO, isAlive)

        if isAlive and ((ethForCall > 0) or (msgValue > 0)):
            with reverts(REV_MSG_NO_ETH_ALIVE):
                auto.r.newReqPaySpecific(target, referer, callData, ethForCall, verifyUser, insertFeeAmount, payWithAUTO, isAlive, {'from': user, 'value': msgValue})
        else:
            tx = auto.r.newReqPaySpecific(target, referer, callData, ethForCall, verifyUser, insertFeeAmount, payWithAUTO, isAlive, {'from': user, 'value': msgValue})

            assert tx.return_value == 0
            print()
            print(tx.events["HashedReqAdded"][0].values())
            print([0, *req])
            assert tx.events["HashedReqAdded"][0].values() == [0, *req]

            hashes = [keccakReq(auto, req)]
            assert auto.r.getHashedReqs() == hashes
            # Should revert when using indexes above the length
            with reverts():
                auto.r.getHashedReqsSlice(0, len(hashes) + 1)
            assert auto.r.getHashedReqsSlice(0, len(hashes)) == hashes
            assert auto.r.getHashedReqsLen() == 1
            assert auto.r.getHashedReq(0) == hashes[0]

            assert auto.r.getHashedReqsUnveri() == []
            # Should revert when using indexes above the length
            with reverts():
                auto.r.getHashedReqsUnveriSlice(0, 1)
            assert auto.r.getHashedReqsUnveriSlice(0, 0) == []
            assert auto.r.getHashedReqsUnveriLen() == 0
            with reverts():
                auto.r.getHashedReqUnveri(0)

            assert user.balance() - userETHStartBal == -msgValue
            assert referer.balance() - refererETHStartBal == 0
            assert target.balance() - targetETHStartBal == 0
            assert auto.r.balance() == msgValue

            assert auto.AUTO.balanceOf(user) - userAUTOStartBal == 0
            assert auto.AUTO.balanceOf(referer) - refererAUTOStartBal == 0
            assert auto.AUTO.balanceOf(target) - targetAUTOStartBal == 0
            assert auto.AUTO.balanceOf(auto.r) == 0

            assert auto.r.getReqCountOf(auto.BOB) == 0
            assert auto.r.getExecCountOf(auto.ALICE) == 0
            assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_newReqPaySpecific_rev_target_is_registry(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.r, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_uf(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.uf, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_ff(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.ff, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_uff(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.uff, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_AUTO(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.AUTO, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_1820_registry(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(ERC1820_REGISTRY_ADDR, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_sm(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(auto.sm, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_target_is_zero_addr(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = auto.r.newReqPaySpecific(ADDR_0, auto.DENICE, callData, 0, False, False, True, False, auto.FR_BOB)


def test_newReqPaySpecific_rev_isAlive_with_eth(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_NO_ETH_ALIVE):
        tx = auto.r.newReqPaySpecific(auto.DENICE, auto.DENICE, callData, 0, False, False, False, True, {'value': E_18, 'from': auto.BOB})


@given(
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
)
def test_newReqPaySpecific_rev_validEth_payWithAUTO(auto, mockTarget, msgValue, ethForCall):
    if msgValue != ethForCall:
        callData = mockTarget.setX.encode_input(5)
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, "", ethForCall, False, False, True, False, {'from': auto.BOB, 'value': msgValue})


@given(
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
)
def test_newReqPaySpecific_rev_validEth_not_payWithAUTO(auto, mockTarget, msgValue, ethForCall):
    ethForCall = msgValue + 1 if ethForCall <= msgValue else ethForCall
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_ETHFORCALL_HIGH):
        tx = auto.r.newReqPaySpecific(mockTarget, auto.DENICE, "", ethForCall, False, False, False, False, {'from': auto.BOB, 'value': msgValue})