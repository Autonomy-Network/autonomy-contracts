# from consts import *
# from brownie.test import given, strategy
# from hypothesis import settings
# from collections import Counter


# numStakes = int((10**8) * E_18 / STAN_STAKE)
# numChunks = 100
# numInChunk = int(numStakes / numChunks)
# MAX_SLICE_LEN = 1000


# @given(
#     stakeChunks=strategy(f'address[{numChunks}]'),
#     startIdx=strategy('uint', max_value=numStakes - 1 - MAX_SLICE_LEN),
#     sliceLen=strategy('uint', max_value=MAX_SLICE_LEN)
# )
# # This test takes forever
# @settings(max_examples=10)
# def test_getStakesSlice(cleanASC, stakeChunks, startIdx, sliceLen):
#     counts = Counter(stakeChunks)
#     for addr, count in counts.items():
#         amount = count * numInChunk * STAN_STAKE
#         cleanASC.ASC.transfer(addr, amount, cleanASC.FR_DEPLOYER)
#         cleanASC.ASC.approve(cleanASC.sm, amount, {'from': addr})

#     stakes = []
#     # Need to split up the tx since it would go over the block gas limit if
#     # we tried to stake everything all at once. Each tx costs a bit under 3m gas
#     for staker in stakeChunks:
#         cleanASC.sm.stake(numInChunk, {'from': staker})
#         stakes += [staker] * numInChunk
    
#     endIdx = startIdx + sliceLen
#     assert cleanASC.sm.getStakesLength() == numStakes
#     assert cleanASC.sm.getStakesSlice(startIdx, endIdx) == stakes[startIdx:endIdx]


# # # This test will fail and timeout because it takes too long to gather the
# # # data, hence the need for getStakesSlice
# # def test_getStakes(cleanASC):
# #     cleanASC.ASC.approve(cleanASC.sm, (10**8) * E_18, cleanASC.FR_DEPLOYER)
# #     # Need to split up the tx since it would go over the block gas limit if
# #     # we tried to stake everything all at once
# #     for i in range(numChunks):
# #         tx = cleanASC.sm.stake(numInChunk, cleanASC.FR_DEPLOYER)
    
# #     assert cleanASC.sm.getStakesLength() == numStakes
# #     assert cleanASC.sm.getStakes() == [cleanASC.DEPLOYER] * numStakes


# # # This test will also fail due to timeout because it reads the same large
# # amount of data
# # @given(
# #     stakeChunks=strategy(f'address[{numChunks}]')
# # )
# # def test_getStakesSlice_all(cleanASC, stakeChunks):
# #     startIdx, endIdx = 0, 9999
# #     if startIdx < endIdx:
# #         counts = Counter(stakeChunks)
# #         for addr, count in counts.items():
# #             amount = count * numInChunk * STAN_STAKE
# #             cleanASC.ASC.transfer(addr, amount, cleanASC.FR_DEPLOYER)
# #             cleanASC.ASC.approve(cleanASC.sm, amount, {'from': addr})

# #         stakes = []
# #         # Need to split up the tx since it would go over the block gas limit if
# #         # we tried to stake everything all at once
# #         for staker in stakeChunks:
# #             cleanASC.sm.stake(numInChunk, {'from': staker})
# #             stakes += [staker] * numInChunk
            
        
# #         assert cleanASC.sm.getStakesLength() == numStakes
# #         assert cleanASC.sm.getStakesSlice(startIdx, endIdx) == stakes[startIdx:endIdx]