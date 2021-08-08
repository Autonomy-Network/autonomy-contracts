from consts import *
from utils import *


# These serve as benchmarks for calibrating GAS_OVERHEAD_ETH and GAS_OVERHEAD_AUTO
# etc experimentally


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases
# def test_gas_usage_rawReq_change_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithArray.encode_input(0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithArray.encode_input(i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithCallData.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithCallData.encode_input([i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndArray.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndArray.encode_input([i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs(auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArray.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArray.encode_input(addrs[:i])
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_specific(auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input([], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input(addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_multiple(auto, mockTarget):
#     addrs = a[:] * 1

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input([], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input(addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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



# payWithAUTO


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasWithArray.encode_input(0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithArray.encode_input(i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call doesn't change, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasWithCallData.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithCallData.encode_input([i for i in range(i)] * 5)
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call increase at a consistent rate, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndArray.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndArray.encode_input([i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call increase at a consistent rate, using addresses instead, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs(a, auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArray.encode_input([])
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArray.encode_input(addrs[:i])
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # actual call increases, but the overall gas of the former is greater than the latter, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs_specific(a, auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input([], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArray.encode_input(addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs_multiple(a, auto, mockTarget):
#     addrs = a[:] * 3

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input([], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 10):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultiple.encode_input(addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, False, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, False, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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











# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases
# def test_gas_usage_rawReq_change_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithArrayVeri.encode_input(auto.BOB, 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithArrayVeri.encode_input(auto.BOB, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasWithCallDataVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasWithCallDataVeri.encode_input(auto.BOB, [i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(auto.BOB, [i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs(auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(auto.BOB, addrs[:i])
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_specific(auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(auto.BOB, [], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(auto.BOB, addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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
# def test_gas_usage_rawReq_change_callData_size_and_call_gas_addrs_multiple(auto, mockTarget):
#     addrs = a[:] * 1

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(auto.BOB, [], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     # print(tx.events["Test"][1].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     diff = tx.return_value - tx.gas_used
#     print(diff)
#     errorPerc = diff / tx.gas_used
#     print(errorPerc)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.BOB.balance()
#         execStartBal = auto.ALICE.balance()
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(auto.BOB, addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, False, E_18, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, False, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB, 'value': E_18})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         ethForExec = getEthForExec(evmMaths, tx, INIT_GAS_PRICE_FAST)
#         ethSpent = (tx.gas_used * tx.gas_price)
#         execProfit = ethForExec - ethSpent
#         assert auto.BOB.balance() - bobStartBal == -ethForExec
#         assert auto.ALICE.balance() - execStartBal == execProfit

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


# payWithAUTO


# # See how gas measurement accuracy changes as calldata size doesn't change and the
# # gas of the actual call increases, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasWithArrayVeri.encode_input(auto.BOB, 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithArrayVeri.encode_input(auto.BOB, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call doesn't change, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasWithCallDataVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasWithCallDataVeri.encode_input(auto.BOB, [i for i in range(i)] * 5)
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call increase at a consistent rate, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas(auto, mockTarget):
#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndArrayVeri.encode_input(auto.BOB, [i for i in range(i)])
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # gas of the actual call increase at a consistent rate, using addresses instead, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs(a, auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(auto.BOB, [])
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 100):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayVeri.encode_input(auto.BOB, addrs[:i])
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # actual call increases, but the overall gas of the former is greater than the latter, while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs_specific(a, auto, mockTarget):
#     addrs = a[:] * 10

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(auto.BOB, [], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

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
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndSpecificAddrArrayVeri.encode_input(auto.BOB, addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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
# # while paying with AUTO
# def test_gas_usage_rawReq_payWithAUTO_change_callData_size_and_call_gas_addrs_multiple(a, auto, mockTarget):
#     addrs = a[:] * 3

#     # Have an initial request executed so that _reqCounts etc are non-zero for the
#     # rest of the test and therefore the only thing to affect gas is how the request
#     # itself changes, since changing a variable from zero costs 20k as opposed to 5k for non-zero
#     auto.AUTO.approve(auto.r, MAX_TEST_STAKE, auto.FR_BOB)
#     callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(auto.BOB, [], 0)
#     req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#     auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#     tx = auto.r.executeHashedReq(0, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#     print(0)
#     # print(tx.events["Test"][0].values())
#     print(tx.gas_used)
#     print(tx.return_value)
#     print(tx.return_value - tx.gas_used)
#     print()

#     for i in range(0, 10):
#         bobStartBal = auto.AUTO.balanceOf(auto.BOB)
#         execStartBal = auto.AUTO.balanceOf(auto.ALICE)
#         # Create request
#         callData = mockTarget.useGasCallDataAndAddrArrayMultipleVeri.encode_input(auto.BOB, addrs, i)
#         req = (auto.BOB.address, mockTarget.address, callData, True, True, 0, 0)
#         auto.r.newHashedReq(mockTarget, callData, True, True, 0, auto.DENICE, *getIpfsMetaData(auto, req), {'from': auto.BOB})

#         tx = auto.r.executeHashedReq(i+1, req, *getIpfsMetaData(auto, req), {'from': auto.ALICE, 'gasPrice': INIT_GAS_PRICE_FAST})

#         AUTOForExec = getAUTOForExec(evmMaths, tx, INIT_AUTO_PER_ETH_WEI, INIT_GAS_PRICE_FAST)
#         assert auto.AUTO.balanceOf(auto.BOB) - bobStartBal == -AUTOForExec
#         assert auto.AUTO.balanceOf(auto.ALICE) - execStartBal == AUTOForExec

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