from consts import *
from utils import *
from brownie import reverts
from brownie.test import given, strategy
from hypothesis import settings


MAX_ARR_LEN = 100
NUM_SLICE_TESTS = 100


@given(
    requesters=strategy(f'address[{MAX_ARR_LEN}]'),
    hashedReqs=strategy(f'bytes32[]', max_length=MAX_ARR_LEN, exclude=bytes(32)),
    startIdxs=strategy(f'uint[{NUM_SLICE_TESTS}]', max_value=MAX_ARR_LEN - 1),
    endIdxs=strategy(f'uint[{NUM_SLICE_TESTS}]', max_value=MAX_ARR_LEN)
)
@settings(max_examples=10)
def test_getHashedReqsUnveriSlice(auto, mockTarget, requesters, hashedReqs, startIdxs, endIdxs):
    hashedReqs = [bytesToHex(h) for h in hashedReqs]
    for h, r in zip(hashedReqs, requesters):
        auto.r.newHashedReqUnveri(h, {'from': r})
    
    assert auto.r.getHashedReqsUnveriSlice(0, len(hashedReqs)) == hashedReqs
    assert auto.r.getHashedReqsUnveriSlice(0, len(hashedReqs)) == auto.r.getHashedReqsUnveri()
    for si, ei in zip(startIdxs, endIdxs):
        if ei < si or (ei > len(hashedReqs) and si != ei):
            with reverts():
                auto.r.getHashedReqsUnveriSlice(si, ei)
        else:
            assert auto.r.getHashedReqsUnveriSlice(si, ei) == hashedReqs[si:ei]
