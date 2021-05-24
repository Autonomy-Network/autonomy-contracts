from consts import *
from utils import *


# These serve as benchmarks for calibrating GAS_OVERHEAD_ETH and GAS_OVERHEAD_ASCOIN
# etc experimentally


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases
# def test_gas_usage_rawReq_change_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithArray.encode_input(0)
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithArray.encode_input(i)
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as calldata size increases and the
# # gas of the actual call doesn't change
# def test_gas_usage_rawReq_change_callData_size(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithCallData.encode_input([])
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithCallData.encode_input([i for i in range(i)])
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate
# def test_gas_usage_rawReq_change_callData_size_and_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndArray.encode_input([])
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndArray.encode_input([i for i in range(i)])
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate, using addresses instead
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs(asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArray.encode_input([])
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArray.encode_input(addrs[:i])
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is greater than the latter
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_specific(asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input([], 0)
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input(addrs, i)
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is lesser than the latter
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_multiple(asc, mockTarget):
#     addrs = a[:] * 3

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input([], 0)
#     asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input(addrs, i)
#         asc.r.newRawReq(mockTarget, callData, False, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()



# payWithASC


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasWithArray.encode_input(0)
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasWithArray.encode_input(i)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 500):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithCallData.encode_input([i for i in range(i)] * 5)
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     addrs = a[:] * 5

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input([], 0)
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input(addrs, i)
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     addrs = a[:] * 1

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input([], 0)
#     asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, False, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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











# -------------------------- VERIFIED USER VERSIONS --------------------------











# # gas of the actual call increases
# def test_gas_usage_rawReq_change_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithArrayVeri.encode_input(asc.BOB, 0)
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithArrayVeri.encode_input(asc.BOB, i)
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as calldata size increases and the
# # gas of the actual call doesn't change
# def test_gas_usage_rawReq_change_callData_size(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithCallDataVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithCallDataVeri.encode_input(asc.BOB, [i for i in range(i)])
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate
# def test_gas_usage_rawReq_change_callData_size_and_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(asc.BOB, [i for i in range(i)])
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as both calldata size increases and the
# # gas of the actual call increase at a consistent rate, using addresses instead
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs(asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(asc.BOB, addrs[:i])
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is greater than the latter
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_specific(asc, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(asc.BOB, [], 0)
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(asc.BOB, addrs, i)
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()


# # See how gas measurement accuracy changes as the calldata is large and the gas of the
# # actual call increases, but the overall gas of the former is lesser than the latter
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_multiple(asc, mockTarget):
#     addrs = a[:] * 1

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(asc.BOB, [], 0)
#     asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = asc.BOB.balance()
#         execStartBal = asc.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(asc.BOB, addrs, i)
#         asc.r.newRawReq(mockTarget, callData, True, False, 0, asc.DENICE, {'from': asc.BOB, 'value': E_18})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert asc.BOB.balance() - bobStartBal == -ethForExec
#         assert asc.ALICE.balance() - execStartBal == execProfit

#         print(i)
#         # print(tx.events["Test"][0].values())
#         # print(tx.events["Test"][1].values())
#         print(tx.gas_used)
#         print(tx.return_value)
#         diff = tx.return_value - tx.gas_used
#         print(diff)
#         errorPerc = diff / tx.gas_used
#         print(errorPerc)
#         print()



# payWithASC


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases, while paying with ASC
# def test_gas_usage_rawReq_payWithASC_change_call_gas(asc, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasWithArrayVeri.encode_input(asc.BOB, 0)
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasWithArrayVeri.encode_input(asc.BOB, i)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     callData = mockTarget.useGasWithCallDataVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 500):
#         bobStartBal = asc.ASC.balanceOf(asc.BOB)
#         execStartBal = asc.ASC.balanceOf(asc.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithCallDataVeri.encode_input(asc.BOB, [i for i in range(i)] * 5)
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(asc.BOB, [i for i in range(i)])
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(asc.BOB, [])
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(asc.BOB, addrs[:i])
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     addrs = a[:] * 5

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(asc.BOB, [], 0)
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(asc.BOB, addrs, i)
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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
#     addrs = a[:] * 1

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     asc.ASC.approve(asc.r, MAX_TEST_STAKE, asc.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(asc.BOB, [], 0)
#     asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
#     tx = asc.r.executeRawReq(0, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(asc.BOB, addrs, i)
#         # print(callData)
#         asc.r.newRawReq(mockTarget, callData, True, True, 0, asc.DENICE, {'from': asc.BOB, 'value': 0})
        
#         tx = asc.r.executeRawReq(i+1, {'from': asc.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ASCForExec = getASCForExec(evmMaths, tx, INIT_AUTO_PER_ETH, INIT_GAS_PRICE_FAST)
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