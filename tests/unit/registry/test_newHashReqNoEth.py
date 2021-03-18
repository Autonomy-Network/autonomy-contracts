from consts import *
from utils import *
from brownie import chain, reverts, web3, convert
from brownie.test import given, strategy
from hashlib import sha256
import ipfshttpclient
import base58 as b58


@given(
    hashedIpfsReq=strategy('bytes32'),
    sender=strategy('address')
)
def test_newHashReqNoEth(asc, mockTarget, hashedIpfsReq, sender):
    tx = asc.r.newHashReqNoEth(hashedIpfsReq)

    assert tx.events["HashedReqNoEthAdded"][0].values() == [0]
    assert tx.return_value == 0
    hashedIpfsReqs = [convert.to_bytes(hash, 'bytes') for hash in asc.r.getHashedIpfsReqsNoEth()]
    assert hashedIpfsReqs == [hashedIpfsReq]
    assert asc.r.getHashedIpfsReqsNoEthLen() == 1
    assert asc.r.getHashedIpfsReqNoEth(0) == bytesToHex(hashedIpfsReq)

    assert asc.r.getRawRequests() == []
    assert asc.r.getRawRequestsLen() == 0
    with reverts():
        asc.r.getRawRequest(0)
    
    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(mockTarget) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL

def test_newHashReqNoEth_real(asc, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    req = (asc.BOB.address, mockTarget, callData, True, 0, 0, asc.DENICE)
    reqBytes = asc.r.getReqBytes(req)

    with ipfshttpclient.connect() as client:
        ipfsCID = client.add_bytes(reqBytes)
        ipfsBlock = client.block.get(ipfsCID)
    
    hash = getHashFromCID(ipfsCID)

    tx = asc.r.newHashReqNoEth(hash)

    assert tx.events["HashedReqNoEthAdded"][0].values() == [0]
    assert tx.return_value == 0
    assert asc.r.getHashedIpfsReqsNoEth() == [hash]
    assert asc.r.getHashedIpfsReqsNoEthLen() == 1
    assert asc.r.getHashedIpfsReqNoEth(0) == getHashFromCID(ipfsCID)

    assert asc.r.getRawRequests() == []
    assert asc.r.getRawRequestsLen() == 0
    with reverts():
        asc.r.getRawRequest(0)
    
    assert asc.r.getHashedIpfsReqsEth() == []
    assert asc.r.getHashedIpfsReqsEthLen() == 0
    with reverts():
        asc.r.getHashedIpfsReqEth(0)

    assert asc.BOB.balance() == INIT_ETH_BAL
    assert asc.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert asc.r.balance() == 0

    assert asc.ASCoin.balanceOf(asc.BOB) == MAX_TEST_STAKE
    assert asc.ASCoin.balanceOf(asc.DENICE) == 0
    assert asc.ASCoin.balanceOf(mockTarget) == 0
    assert asc.ASCoin.balanceOf(asc.r) == INIT_ASC_REW_POOL


    # Ensure that the hash used with newHashReqNoEth is the same as 
    # the one generated with newHashReqWithEth
    reqBytesIdx = ipfsBlock.index(reqBytes)
    dataPrefix = ipfsBlock[:reqBytesIdx]
    dataSuffix = ipfsBlock[reqBytesIdx + len(reqBytes) : ]

    tx2 = asc.r.newHashReqWithEth(mockTarget, callData, True, 0, asc.DENICE, dataPrefix, dataSuffix, asc.FR_BOB)

    assert asc.r.getHashedIpfsReqEth(0) == hash

# import time
# # Ensure that everything still works
# def test_newHashReqNoEth_spam(asc):
#     t0 = time.time()
#     for i in range(1, 100001):
#         t1 = time.time()
#         # print(i)

#         t2 = time.time()
#         asc.r.newHashReqNoEth(i)
#         # print(f'newHashReqNoEth = {(time.time()-t2)}')

#         if i % 1000 == 0:
#             print(f'i = {i}')
#             t2 = time.time()
#             # asc.r.getHashedIpfsReqsNoEth()
#             # print(f'getHashedIpfsReqsNoEth = {(time.time()-t2)}')

#             reqs = []
#             for i in range(asc.r.getHashedIpfsReqsNoEthLen()):
#                 reqs.append(asc.r.getHashedIpfsReqNoEth(i))
#             # print(reqs)
#             print(f'getHashedIpfsReqNoEth total = {(time.time()-t2)}')
#             print(f'getHashedIpfsReqsNoEth per req  = {(time.time()-t2) / i}')
#             print()

#         # t2 = time.time()
#         # asc.r.getHashedIpfsReqsNoEthLen()
#         # print(f'getHashedIpfsReqsNoEthLen = {(time.time()-t2)}')

#         # print(f'totalRate = {(time.time()-t0)/i}')
#         # print(f'singleRate = {(time.time()-t1)}')
#         # print()


