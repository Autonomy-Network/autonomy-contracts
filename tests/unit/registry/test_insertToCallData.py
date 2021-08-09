from consts import *
from brownie.test import given, strategy
from utils import *


@given(num=strategy('uint256'))
def test_insertToCallData_4(auto, mockTarget, num):
    callData = mockTarget.setX.encode_input(5)
    modifiedCallData = auto.r.insertToCallData(callData, num, 4)
    
    assert modifiedCallData == callData[:10] + hexStrPad(num)

    newCallData = mockTarget.setX.encode_input(num)

    assert modifiedCallData == newCallData

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

    inputs = (addr, num)
    newCallData = mockTarget.setXAddr.encode_input(*inputs)

    assert modifiedCallData == newCallData

    mockTarget.setXAddr(*inputs)

    assert mockTarget.userAddr() == addr
    assert mockTarget.x() == num


@given(
    addr=strategy('address'),
    num=strategy('uint256')
)
def test_insertToCallData_36_with_extra_inputs(auto, mockTarget, addr, num):
    callData = mockTarget.setXAddrWithArr.encode_input(addr, 5, [69, 420])
    modifiedCallData = auto.r.insertToCallData(callData, num, 36)
    
    # assert modifiedCallData == callData[:74] + hexStrPad(num)

    inputs = (addr, num, [69, 420])
    newCallData = mockTarget.setXAddrWithArr.encode_input(*inputs)

    assert modifiedCallData == newCallData

    mockTarget.setXAddrWithArr(*inputs)

    assert mockTarget.userAddr() == addr
    assert mockTarget.x() == num