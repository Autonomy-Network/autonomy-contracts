from consts import *
from brownie.test import given, strategy
from utils import *


@given(num=strategy('uint256'))
def test_insertToCallData_4(auto, mockTarget, num):
    callData = mockTarget.setX.encode_input(5)
    modifiedCallData = auto.r.insertToCallData(callData, num, 4)
    
    assert modifiedCallData == callData[:10] + hexStrPad(num)

    mockTarget.setX(num)

    assert mockTarget.x() == num


@given(
    addr=strategy('address'),
    num=strategy('uint256')
)
def test_insertToCallData_36(auto, mockTarget, addr, num):
    callData = mockTarget.setXAddr.encode_input(addr, 5)
    modifiedCallData = auto.r.insertToCallData(callData, num, 36)
    
    assert modifiedCallData == callData[:74] + hexStrPad(num)

    mockTarget.setXAddr(addr, num)

    assert mockTarget.userAddr() == addr
    assert mockTarget.x() == num