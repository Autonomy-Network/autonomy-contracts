from consts import *
from brownie import a, reverts, Contract
import time


def test_limitOrder(asc, stakedMin, MockUniLimit):
    _, staker, __ = stakedMin

    MOCK_UNI_LIMIT = asc.DEPLOYER.deploy(MockUniLimit, asc.vf)
    WETH_ADDR = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    ANY_ADDR = '0xf99d58e463A2E07e5692127302C20A191861b4D6'
    WHALE = a.at('0xCA81dBbBb9389A5387f0aCad4d018756A04d7f2C', force=True)
    ANY = Contract.from_explorer(ANY_ADDR)
    UNI_ROUTER_2 = Contract.from_explorer('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
    asc.ASC.approve(asc.r, 2**255, asc.FR_CHARLIE)

    # For 0.1 ETH
    path = [WETH_ADDR, ANY_ADDR]
    inputAmount = int(0.1 * E_18)
    currentOutput = UNI_ROUTER_2.getAmountsOut(inputAmount, path)[-1]
    limitOutput = int(currentOutput * 1.2)
    callData = MOCK_UNI_LIMIT.ethToTokenLimitOrder.encode_input(asc.CHARLIE, limitOutput, path, asc.CHARLIE, time.time() * 2)

    # Make the request
    asc.r.newRawReq(MOCK_UNI_LIMIT, callData, True, True, inputAmount, ADDR_0, 
        {'value': inputAmount, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': asc.CHARLIE})

    # Check that the request reverts without the condition being fulfilled
    with reverts('UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT'):
        asc.r.executeRawReq(0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Send ANY to the Uniswap contract to make the price of ANY much cheaper
    token_amount = 10**22
    ANY.approve(UNI_ROUTER_2, token_amount, {'from': WHALE})
    UNI_ROUTER_2.swapExactTokensForETH(token_amount, 1, [ANY_ADDR, WETH_ADDR], WHALE, time.time()*2, {'from': WHALE})

    # Execute successfully :D
    anyStartBal = ANY.balanceOf(asc.CHARLIE)
    asc.r.executeRawReq(0, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    anyEndBal = ANY.balanceOf(asc.CHARLIE)
    assert anyStartBal < anyEndBal
    print(anyStartBal, anyEndBal)


    # For 1 ANY
    inputAmount = E_18
    path = [ANY_ADDR, WETH_ADDR]
    currentOutput = UNI_ROUTER_2.getAmountsOut(inputAmount, path)[-1]
    limitOutput = int(currentOutput * 1.2)
    callData = MOCK_UNI_LIMIT.tokenToEthLimitOrder.encode_input(asc.CHARLIE, inputAmount, limitOutput, path, asc.CHARLIE, time.time() * 2)

    # Make the request
    asc.r.newRawReq(MOCK_UNI_LIMIT, callData, True, True, 0, ADDR_0, 
        {'value': 0, 'gasPrice': INIT_GAS_PRICE_FAST, 'from': asc.CHARLIE})
    ANY.approve(MOCK_UNI_LIMIT, inputAmount, asc.FR_CHARLIE)

    # Check that the request reverts without the condition being fulfilled
    with reverts('UniswapV2Router: INSUFFICIENT_OUTPUT_AMOUNT'):
        asc.r.executeRawReq(1, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST})
    
    # Send ETH to the Uniswap contract to make the price of ETH much cheaper
    eth_amount = 10**19
    UNI_ROUTER_2.swapExactETHForTokens(1, [WETH_ADDR, ANY_ADDR], WHALE, time.time()*2, {'value': eth_amount, 'from': WHALE})
    
    # Execute successfully :D
    ethStartBal = asc.CHARLIE.balance()
    gasUsed = asc.r.executeRawReq(1, {'from': staker, 'gasPrice': INIT_GAS_PRICE_FAST}).return_value
    ethEndBal = asc.CHARLIE.balance()
    print(ethStartBal, ethEndBal)
    assert ethStartBal < ethEndBal