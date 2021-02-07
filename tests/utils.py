from consts import *
from brownie import web3


def getEpoch(blockNum):
    return int(blockNum / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH


def getRandNum(seed):
    num = int(web3.toInt(web3.eth.getBlock(seed).hash) / NORM_FACTOR)
    assert num <= E_18
    return num


def getExecutor(blockNum, stakers):
    epoch = getEpoch(blockNum)
    randNum = getRandNum(epoch)
    i = int(randNum * len(stakers) / E_18)
    print('Internal getxecutor', randNum/E_18, i, stakers[i])
    return stakers[i], epoch


def getModStakes(stakes, staker, numStakes, isStaking):
    if isStaking:
        return stakes + ([staker] * numStakes)
    else:
        print(isStaking)
        cntr = 0
        # Iterate through backwards
        for i in range(len(stakes)-1, -1 , -1):
        # while cntr < numStakes:
            print(i)
            if stakes[-i] == staker:
                stakes[-i] = stakes[len(stakes)-1]
                stakes = stakes[:-1]
                cntr += 1
            if cntr == numStakes:
                break
        
        return stakes