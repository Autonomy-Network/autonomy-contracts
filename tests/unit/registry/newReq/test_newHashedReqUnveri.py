from consts import *
from utils import *
from brownie import chain, reverts, web3, convert
from brownie.test import given, strategy
from hashlib import sha256
import ipfshttpclient
import base58 as b58


@given(
    hashedIpfsReq=strategy('bytes32', exclude=bytes(32)),
    sender=strategy('address')
)
def test_newHashedReqUnveri(asc, mockTarget, hashedIpfsReq, sender):
    tx = asc.r.newHashedReqUnveri(hashedIpfsReq)

    assert tx.events["HashedReqUnveriAdded"][0].values() == [0]
    assert tx.return_value == 0
    hashedIpfsReqs = [convert.to_bytes(hash, 'bytes') for hash in asc.r.getHashedReqsUnveri()]
    assert hashedIpfsReqs == [hashedIpfsReq]
    assert asc.r.getHashedReqsUnveriLen() == 1
    assert asc.r.getHashedReqUnveri(0) == bytesToHex(hashedIpfsReq)

    assert asc.r.getRawReqs() == []
    assert asc.r.getRawReqLen() == 0
    with reverts():
        asc.r.getRawReq(0)
    
    assert asc.r.getHashedReqs() == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0

def test_newHashedReqUnveri_real(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget, callData, False, True, 0, 0, asc.DENICE)
    reqBytes = asc.r.getReqBytes(req)

    with ipfshttpclient.connect() as client:
        ipfsCID = client.add_bytes(reqBytes)
        ipfsBlock = client.block.get(ipfsCID)
    
    hash = getHashFromCID(ipfsCID)

    tx = asc.r.newHashedReqUnveri(hash)

    assert tx.events["HashedReqUnveriAdded"][0].values() == [0]
    assert tx.return_value == 0
    assert asc.r.getHashedReqsUnveri() == [hash]
    assert asc.r.getHashedReqsUnveriLen() == 1
    assert asc.r.getHashedReqUnveri(0) == getHashFromCID(ipfsCID)

    assert asc.r.getRawReqs() == []
    assert asc.r.getRawReqLen() == 0
    with reverts():
        asc.r.getRawReq(0)
    
    assert asc.r.getHashedReqs() == []
    assert asc.r.getHashedReqsLen() == 0
    with reverts():
        asc.r.getHashedReq(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASC.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASC.balanceOf(asc.DENICE) == 0
    assert asc.ASC.balanceOf(mockTarget) == 0
    assert asc.ASC.balanceOf(asc.r) == 0

    assert asc.r.getReqCountOf(asc.BOB) == 0
    assert asc.r.getExecCountOf(asc.ALICE) == 0
    assert asc.r.getReferalCountOf(asc.DENICE) == 0


    # Ensure that the hash used with newHashedReqUnveri is the same as 
    # the one generated with newHashedReq
    reqBytesIdx = ipfsBlock.index(reqBytes)
    dataPrefix = ipfsBlock[:reqBytesIdx]
    dataSuffix = ipfsBlock[reqBytesIdx + len(reqBytes) : ]

    tx2 = asc.r.newHashedReq(mockTarget, callData, False, True, 0, asc.DENICE, dataPrefix, dataSuffix, asc.FR_BOB)

    assert asc.r.getHashedReq(0) == hash


def test_newHashedReqUnveri_rev_empty_hashedIpfsReq(asc, mockTarget):
    with reverts(REV_MSG_NZ_BYTES32):
        asc.r.newHashedReqUnveri("")


# import time
# # Ensure that everything still works
# def test_newHashedReqUnveri_spam(asc):
#     t0 = time.time()
#     for i in range(1, 100001):
#         t1 = time.time()
#         # print(i)

#         t2 = time.time()
#         asc.r.newHashedReqUnveri(i)
#         # print(f'newHashedReqUnveri = {(time.time()-t2)}')

#         if i % 1000 == 0:
#             print(f'i = {i}')
#             t2 = time.time()
#             # asc.r.getHashedReqsUnveri()
#             # print(f'getHashedReqsUnveri = {(time.time()-t2)}')

#             reqs = []
#             for i in range(asc.r.getHashedReqsUnveriLen()):
#                 reqs.append(asc.r.getHashedReqUnveri(i))
#             # print(reqs)
#             print(f'getHashedReqUnveri total = {(time.time()-t2)}')
#             print(f'getHashedReqsUnveri per req  = {(time.time()-t2) / i}')
#             print()

#         # t2 = time.time()
#         # asc.r.getHashedReqsUnveriLen()
#         # print(f'getHashedReqsUnveriLen = {(time.time()-t2)}')

#         # print(f'totalRate = {(time.time()-t0)/i}')
#         # print(f'singleRate = {(time.time()-t1)}')
#         # print()


