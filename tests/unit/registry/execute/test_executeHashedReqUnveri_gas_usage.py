from consts import *
from utils import *


# These serve as benchmarks for calibrating GAS_OVERHEAD_ETH and GAS_OVERHEAD_ASCOIN
# etc experimentally


# payWithASC


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasWithArray.encode_input(0)
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithArray.encode_input(i)
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()
    

# # See how gas measurement accuracy changes as calldata size increases and the
# # gas of the actual call doesn't change, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_callData_size(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasWithCallData.encode_input([])
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 500):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithCallData.encode_input([i for i in range(i)] * 5)
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()
    

# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_callData_size_and_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndArray.encode_input([])
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndArray.encode_input([i for i in range(i)])
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate, using addresses instead, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_callData_size_and_call_gas_addrs(a, asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArray.encode_input([])
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArray.encode_input(addrs[:i])
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is greater than the latter, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_callData_size_and_call_gas_addrs_specific(a, asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input([], 0)
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input(addrs, i)
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is lesser than the latter,
# # while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_callData_size_and_call_gas_addrs_multiple(a, asc, mockTarget):
#     addrs = a[:] * 3

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input([], 0)
#     req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#     reqHashBytes = addReqGetHashBytes(asc, req)
#     asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#     tx = asc.r.executeHashedReqUnveri(0, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 10):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input(addrs, i)
#         req = (asc.BOB.address, mockTarget.address, callData, False, True, 0, 0, asc.DENICE.address)
#         reqHashBytes = addReqGetHashBytes(asc, req)
#         asc.r.newHashedReqUnveri(reqHashBytes, {'from': asc.BOB, 'value': 0})

#         tx = asc.r.executeHashedReqUnveri(i+1, req, *getIpfsMetaData(asc, req), {'from': asc.ALICE, 'gasPrice': TEST_GAS_PRICE})

#         ASCForExec = getASCForExec(asc, tx, INIT_ETH_PER_USD, INIT_ASC_PER_USD)
#         assert asc.ASC.balanceOf(asc.BOB) - bobStartBal == -ASCForExec
#         assert asc.ASC.balanceOf(asc.ALICE) - execStartBal == ASCForExec

#         print(i)
#         # print(tx.events["Test"][0].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         # assert 0 <= errorPerc <= MAX_ERROR_FACTOR
#         print()