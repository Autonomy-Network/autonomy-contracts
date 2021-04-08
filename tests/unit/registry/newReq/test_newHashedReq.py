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
    callData=strategy('bytes'),
    verifySender=strategy('bool'),
    payWithASC=strategy('bool'),
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
    referer=strategy('address')
)
def test_newHashedReq(asc, mockTarget, user, target, callData, verifySender, payWithASC, msgValue, ethForCall, referer):
    if user != target and user != referer:
        # assert user.balance() == INIT_ETH_BAL
        userETHStartBal = user.balance()
        # assert referer.balance() == INIT_ETH_BAL
        refererETHStartBal = referer.balance()
        # assert target.balance() == 0
        targetETHStartBal = target.balance()
        assert asc.r.balance() == 0

        # assert asc.ASC.balanceOf(user) == MAX_TEST_STAKE
        userASCStartBal = asc.ASC.balanceOf(user)
        # assert asc.ASC.balanceOf(referer) == 0
        refererASCStartBal = asc.ASC.balanceOf(referer)
        # assert asc.ASC.balanceOf(target) == 0
        targetASCStartBal = asc.ASC.balanceOf(target)
        assert asc.ASC.balanceOf(asc.r) == 0

        if payWithASC:
            msgValue = ethForCall
        else:
            msgValue = ethForCall if msgValue < ethForCall else msgValue

        req = (user, target, callData, verifySender, payWithASC, msgValue, ethForCall, referer)
        reqBytes = asc.r.getReqBytes(req)
        
        with ipfshttpclient.connect() as client:
            ipfsCID = client.add_bytes(reqBytes)
            ipfsBlock = client.block.get(ipfsCID)
        
        reqBytesIdx = ipfsBlock.index(reqBytes)
        dataPrefix = ipfsBlock[:reqBytesIdx]
        dataSuffix = ipfsBlock[reqBytesIdx + len(reqBytes) : ]

        tx = asc.r.newHashedReq(target, callData, verifySender, payWithASC, ethForCall, referer, dataPrefix, dataSuffix, {'from': user, 'value': msgValue})

        assert tx.return_value == 0
        assert tx.events["HashedReqAdded"][0].values() == [0]
        b58HashedIpfsReqs = [getCID(hash) for hash in asc.r.getHashedReqs()]
        assert b58HashedIpfsReqs == [ipfsCID]
        assert asc.r.getHashedReqsLen() == 1
        assert asc.r.getHashedReq(0) == getHashFromCID(ipfsCID)

        assert asc.r.getRawReqs() == []
        assert asc.r.getRawReqLen() == 0
        with reverts():
            asc.r.getRawReq(0)
        
        assert asc.r.getHashedReqsUnveri() == []
        assert asc.r.getHashedReqsUnveriLen() == 0
        with reverts():
            asc.r.getHashedReqUnveri(0)

        assert user.balance() - userETHStartBal == -msgValue
        assert referer.balance() - refererETHStartBal == 0
        assert target.balance() - targetETHStartBal == 0
        assert asc.r.balance() == msgValue

        assert asc.ASC.balanceOf(user) - userASCStartBal == 0
        assert asc.ASC.balanceOf(referer) - refererASCStartBal == 0
        assert asc.ASC.balanceOf(target) - targetASCStartBal == 0
        assert asc.ASC.balanceOf(asc.r) == 0

        assert asc.r.getReqCountOf(asc.BOB) == 0
        assert asc.r.getExecCountOf(asc.ALICE) == 0
        assert asc.r.getReferalCountOf(asc.DENICE) == 0


def test_newHashedReq_rev_target_is_registry(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = asc.r.newHashedReq(asc.r, callData, False, True, 0, asc.DENICE, "", "", asc.FR_BOB)


def test_newHashedReq_rev_target_is_ASCoin(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_TARGET):
        tx = asc.r.newHashedReq(asc.r, callData, False, True, 0, asc.DENICE, "", "", asc.FR_BOB)


@given(
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
)
def test_newHashedReq_rev_validEth_payWithASC(asc, mockTarget, msgValue, ethForCall):
    if msgValue != ethForCall:
        callData = mockTarget.setX.encode_input(5)
        with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
            tx = asc.r.newHashedReq(mockTarget, "", False, True, ethForCall, asc.DENICE, "", "", {'from': asc.BOB, 'value': msgValue})


@given(
    msgValue=strategy('uint256', max_value=E_18),
    ethForCall=strategy('uint256', max_value=E_18),
)
def test_newHashedReq_rev_validEth_not_payWithASC(asc, mockTarget, msgValue, ethForCall):
    ethForCall = msgValue + 1 if ethForCall <= msgValue else ethForCall
    callData = mockTarget.setX.encode_input(5)
    with reverts(REV_MSG_ETHFORCALL_HIGH):
        tx = asc.r.newHashedReq(mockTarget, "", False, False, ethForCall, asc.DENICE, "", "", {'from': asc.BOB, 'value': msgValue})