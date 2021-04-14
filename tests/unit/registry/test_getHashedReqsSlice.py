from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy
from hypothesis import settings


MAX_ARR_LEN = 100
NUM_SLICE_TESTS = 100


@given(
    requesters=strategy('address[]', max_length=MAX_ARR_LEN),
    startIdxs=strategy(f'uint[{NUM_SLICE_TESTS}]', max_value=MAX_ARR_LEN - 1),
    endIdxs=strategy(f'uint[{NUM_SLICE_TESTS}]', max_value=MAX_ARR_LEN)
)
@settings(max_examples=10)
def test_getHashedReqsSlice(asc, mockTarget, requesters, startIdxs, endIdxs):
    callData = mockTarget.setX.encode_input(5)
    hashedReqs = []
    for requester in requesters:
        req = (requester.address, mockTarget.address, callData, False, False, 0, 0, asc.DENICE.address)
        cid = addToIpfs(asc, req)
        asc.r.newHashedReq(mockTarget, callData, False, False, 0, asc.DENICE, *getIpfsMetaData(asc, req), {'from': requester})
        hashedReqs.append(getHashFromCID(cid))
    
    assert asc.r.getHashedReqsSlice(0, len(requesters)) == hashedReqs
    assert asc.r.getHashedReqsSlice(0, len(requesters)) == asc.r.getHashedReqs()
    for si, ei in zip(startIdxs, endIdxs):
        if ei < si or (ei > len(requesters) and si != ei):
            with reverts():
                asc.r.getHashedReqsSlice(si, ei)
        else:
            assert asc.r.getHashedReqsSlice(si, ei) == hashedReqs[si:ei]
