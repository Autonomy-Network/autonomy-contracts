from consts import *
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
def test_getRawReqsSlice(asc, mockTarget, requesters, startIdxs, endIdxs):
    callData = mockTarget.setX.encode_input(5)
    reqs = []
    for requester in requesters:
        asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': requester})
        reqs.append((requester.address, mockTarget.address, callData, False, False, 0, 0, asc.DENICE.address))
    
    assert asc.r.getRawReqsSlice(0, len(requesters)) == reqs
    assert asc.r.getRawReqsSlice(0, len(requesters)) == asc.r.getRawReqs()
    for si, ei in zip(startIdxs, endIdxs):
        if ei < si or (ei > len(requesters) and si != ei):
            with reverts():
                asc.r.getRawReqsSlice(si, ei)
        else:
            assert asc.r.getRawReqsSlice(si, ei) == reqs[si:ei]