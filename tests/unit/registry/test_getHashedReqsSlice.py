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
def test_getHashedReqsSlice(auto, mockTarget, requesters, startIdxs, endIdxs):
    callData = mockTarget.setX.encode_input(5)
    hashedReqs = []
    for requester in requesters:
        req = (requester.address, mockTarget.address, auto.DENICE, callData, 0, 0, False, False, False, False)
        cid = addToIpfs(auto, req)
        auto.r.newReqPaySpecific(mockTarget, auto.DENICE, callData, 0, False, False, False, False, {'from': requester})
        hashedReqs.append(keccakReq(auto, req))

    
    assert auto.r.getHashedReqsSlice(0, len(requesters)) == hashedReqs
    assert auto.r.getHashedReqsSlice(0, len(requesters)) == auto.r.getHashedReqs()
    for si, ei in zip(startIdxs, endIdxs):
        if ei < si or (ei > len(requesters) and si != ei):
            with reverts():
                auto.r.getHashedReqsSlice(si, ei)
        else:
            assert auto.r.getHashedReqsSlice(si, ei) == hashedReqs[si:ei]
