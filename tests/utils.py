from consts import *
from brownie import web3


def getEpoch(blockNum):
    return int(blockNum / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH


def getRandNum(seed):
    return web3.toInt(web3.eth.getBlock(seed).hash)


def getExecutor(asc, blockNum, stakers):
    epoch = getEpoch(blockNum)
    randNum = getRandNum(epoch)
    # i = randNum % len(stakers)
    i = asc.sm.getRemainder(randNum, len(stakers))
    print(epoch, randNum, i)
    return stakers[i], epoch


def getFirstIndexes(stakes, val, n):
    cntr = 0
    idxs = []

    for i in range(n):
        idx = stakes.index(val)
        idxs.append(idx)
        stakes[idx] = stakes[-1]
        stakes = stakes[:-1]


    # for i, el in enumerate(stakes):
    #     if el == val:
    #         idxs.append(i)
    #         cntr += 1
    #         if cntr == n:
    #             break
    
    
    # Shouldn't be a situation where fewer occurances are
    # found than expected
    assert len(idxs) == n

    return idxs


def getModStakes(stakes, staker, numStakes, isStaking):
    if isStaking:
        return stakes + ([staker] * numStakes)
    else:
        idxs = []
        for i in range(numStakes):
            idx = stakes.index(staker)
            idxs.append(idx)
            stakes[idx] = stakes[-1]
            stakes = stakes[:-1]

        assert len(idxs) == numStakes
        return idxs, stakes
        abbccb