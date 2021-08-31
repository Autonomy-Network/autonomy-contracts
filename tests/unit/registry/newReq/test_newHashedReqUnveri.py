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
def test_newHashedReqUnveri(auto, mockTarget, hashedIpfsReq, sender):
    tx = auto.r.newHashedReqUnveri(hashedIpfsReq)

    assert tx.events["HashedReqUnveriAdded"][0].values() == [0]
    assert tx.return_value == 0
    hashedIpfsReqs = [convert.to_bytes(hash, 'bytes') for hash in auto.r.getHashedReqsUnveri()]
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, len(hashedIpfsReqs) + 1)
    assert [convert.to_bytes(hash, 'bytes') for hash in auto.r.getHashedReqsUnveriSlice(0, len(hashedIpfsReqs))] == hashedIpfsReqs
    assert hashedIpfsReqs == [hashedIpfsReq]
    assert auto.r.getHashedReqsUnveriLen() == 1
    assert auto.r.getHashedReqUnveri(0) == bytesToHex(hashedIpfsReq)

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsSlice(0, 0) == []
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)

    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert auto.r.balance() == 0

    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0

def test_newHashedReqUnveri_real(auto, mockTarget):
    callData = mockTarget.setX.encode_input(5)
    req = (auto.BOB.address, mockTarget, auto.DENICE, callData, 0, 0, False, False, True, False)
    reqBytes = auto.r.getReqBytes(req)

    with ipfshttpclient.connect() as client:
        ipfsCID = client.add_bytes(reqBytes)
        ipfsBlock = client.block.get(ipfsCID)
    
    hash = getHashFromCID(ipfsCID)

    tx = auto.r.newHashedReqUnveri(hash)

    assert tx.events["HashedReqUnveriAdded"][0].values() == [0]
    assert tx.return_value == 0
    reqHashesUnveri = [hash]
    assert auto.r.getHashedReqsUnveri() == reqHashesUnveri
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri) + 1)
    assert auto.r.getHashedReqsUnveriSlice(0, len(reqHashesUnveri)) == reqHashesUnveri
    assert auto.r.getHashedReqsUnveriLen() == 1
    assert auto.r.getHashedReqUnveri(0) == getHashFromCID(ipfsCID)

    assert auto.r.getHashedReqs() == []
    # Should revert when using indexes above the length
    with reverts():
        auto.r.getHashedReqsSlice(0, 1)
    assert auto.r.getHashedReqsSlice(0, 0) == []
    assert auto.r.getHashedReqsLen() == 0
    with reverts():
        auto.r.getHashedReq(0)

    assert auto.BOB.balance() == INIT_ETH_BAL
    assert auto.DENICE.balance() == INIT_ETH_BAL
    assert mockTarget.balance() == 0
    assert auto.r.balance() == 0

    assert auto.AUTO.balanceOf(auto.BOB) == MAX_TEST_STAKE
    assert auto.AUTO.balanceOf(auto.DENICE) == 0
    assert auto.AUTO.balanceOf(mockTarget) == 0
    assert auto.AUTO.balanceOf(auto.r) == 0

    assert auto.r.getReqCountOf(auto.BOB) == 0
    assert auto.r.getExecCountOf(auto.ALICE) == 0
    assert auto.r.getReferalCountOf(auto.DENICE) == 0


def test_newHashedReqUnveri_rev_empty_hashedIpfsReq(auto, mockTarget):
    with reverts(REV_MSG_NZ_BYTES32):
        auto.r.newHashedReqUnveri("")


# import time
# # Ensure that everything still works
# def test_newHashedReqUnveri_spam(auto):
#     t0 = time.time()
#     for i in range(1, 100001):
#         t1 = time.time()
#         # print(i)

#         t2 = time.time()
#         auto.r.newHashedReqUnveri(i)
#         # print(f'newHashedReqUnveri = {(time.time()-t2)}')

#         if i % 1000 == 0:
#             print(f'i = {i}')
#             t2 = time.time()
#             # auto.r.getHashedReqsUnveri()
#             # print(f'getHashedReqsUnveri = {(time.time()-t2)}')

#             reqs = []
#             for i in range(auto.r.getHashedReqsUnveriLen()):
#                 reqs.append(auto.r.getHashedReqUnveri(i))
#             # print(reqs)
#             print(f'getHashedReqUnveri total = {(time.time()-t2)}')
#             print(f'getHashedReqsUnveri per req  = {(time.time()-t2) / i}')
#             print()

#         # t2 = time.time()
#         # auto.r.getHashedReqsUnveriLen()
#         # print(f'getHashedReqsUnveriLen = {(time.time()-t2)}')

#         # print(f'totalRate = {(time.time()-t0)/i}')
#         # print(f'singleRate = {(time.time()-t1)}')
#         # print()


