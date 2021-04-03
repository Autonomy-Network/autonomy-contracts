from consts import *
from utils import *
from brownie import chain, reverts, web3, convert
from brownie.test import given, strategy
import ipfshttpclient
import binascii
from hashlib import sha256
import base58 as b58


@given(
    bytes_a=strategy('bytes'),
    bytes_b=strategy('bytes'),
    bytes_c=strategy('bytes'),
)
def test_getIpfsReqBytes(asc, bytes_a, bytes_b, bytes_c):
    localBytes = bytes_a + bytes_b + bytes_c
    solidityBytes = convert.to_bytes(asc.r.getIpfsReqBytes(bytes_a, bytes_b, bytes_c), 'bytes')

    assert localBytes == solidityBytes


@given(
    bytes_a=strategy('bytes'),
    bytes_b=strategy('bytes'),
    bytes_c=strategy('bytes'),
)
def test_getHashedIpfsReq(asc, bytes_a, bytes_b, bytes_c):
    localHash = sha256(bytes_a + bytes_b + bytes_c).digest()
    solidityHash = convert.to_bytes(asc.r.getHashedIpfsReq(bytes_a, bytes_b, bytes_c), 'bytes')

    assert localHash == solidityHash


def test_recreate_request_CID(asc, reqsRaw):
    for i in range(asc.r.getRawRequestsLen()):
        req = asc.r.getRawRequest(1)
        reqBytes = convert.to_bytes(asc.r.getReqBytes(req), 'bytes')
        
        with ipfshttpclient.connect() as client:
            ipfsCID= client.add_bytes(reqBytes)
            ipfsBlock = client.block.get(ipfsCID)
        
        reqBytesIdx = ipfsBlock.index(reqBytes)
        dataPrefix = ipfsBlock[:reqBytesIdx]
        dataSuffix = ipfsBlock[reqBytesIdx + len(reqBytes) : ]
        ipfsHash = asc.r.getHashedIpfsReq(dataPrefix, reqBytes, dataSuffix)
        cidHex = CID_PREFIX_BYTES + ipfsHash
        cid = str(b58.b58encode(cidHex), 'ascii')

        assert ipfsCID == cid


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
def test_getReqFromBytes(asc, mockTarget, user, target, callData, verifySender, payWithASC, msgValue, ethForCall, referer):
    req = (user, target, bytesToHex(callData), verifySender, payWithASC, msgValue, ethForCall, referer)
    reqBytes = asc.r.getReqBytes(req)
    
    assert asc.r.getReqFromBytes(reqBytes) == req