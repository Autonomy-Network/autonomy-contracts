from consts import *
from brownie import web3, convert
import base58 as b58
import ipfshttpclient
from hashlib import sha256


def getEpoch(blockNum):
    return int(blockNum / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH


def getRandNum(seed):
    return web3.toInt(web3.eth.get_block(seed).hash)


def getExecutor(evmMaths, blockNum, stakes):
    epoch = getEpoch(blockNum)
    # -1 because blockhash(seed) in Oracle will return 0x00 if the
    # seed == this block's height
    randNum = getRandNum(epoch - 1)
    # i = randNum % len(stakes)
    i = evmMaths.getRemainder(randNum, len(stakes))
    # print(randNum, epoch, i, stakes[i], stakes)
    return stakes[i], epoch


def getUpdatedExecResult(evmMaths, curHeight, stakes):
    epoch = getEpoch(web3.eth.block_number)
    randNum = getRandNum(epoch - 1)
    idx = evmMaths.getRemainder(randNum, len(stakes))

    return (epoch, randNum, idx, stakes[idx])


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
        newStakes = list(stakes)
        for i in range(numStakes):
            idx = newStakes.index(staker)
            idxs.append(idx)
            newStakes[idx] = newStakes[-1]
            newStakes = newStakes[:-1]

        assert len(idxs) == numStakes
        return idxs, newStakes


# Assumes a sha256 hash of (prefix + data + suffix) is the input
def getCID(hash):
    if type(hash) is not bytes:
        hash = convert.to_bytes(hash, 'bytes')
    cidBytes = CID_PREFIX_BYTES + hash
    return str(b58.b58encode(cidBytes), 'ascii')


def bytesToHex(b):
    return '0x' + b.hex()


def getHashBytesFromCID(CID):
    return b58.b58decode(CID)[2:]


def getHashFromCID(CID):
    return bytesToHex(b58.b58decode(CID)[2:])


def addToIpfs(auto, req):
    reqBytes = auto.r.getReqBytes(req)

    with ipfshttpclient.connect() as client:
        return client.add_bytes(reqBytes)


def getIpfsMetaData(auto, req):
    reqBytes = auto.r.getReqBytes(req)

    with ipfshttpclient.connect() as client:
        ipfsCID = client.add_bytes(reqBytes)
        ipfsBlock = client.block.get(ipfsCID)
    
    reqBytesIdx = ipfsBlock.index(reqBytes)
    dataPrefix = ipfsBlock[:reqBytesIdx]
    dataSuffix = ipfsBlock[reqBytesIdx + len(reqBytes) : ]

    return dataPrefix, dataSuffix


def addReqGetHashBytes(auto, req):
    return getHashBytesFromCID(addToIpfs(auto, req))


def getEthForExec(evmMaths, tx, gasPriceFast):
    return evmMaths.mul3div1(tx.return_value, gasPriceFast, PAY_ETH_BPS, BASE_BPS)


def getAUTOForExec(evmMaths, tx, AUTOPerETH, gasPriceFast):
    # Need to account for differences in division between Python and Solidity
    return evmMaths.mul4Div2(tx.return_value, gasPriceFast, AUTOPerETH, PAY_AUTO_BPS, BASE_BPS, E_18)


def checkAreCallers(auto, addrs, callers):
    print()
    print(callers)
    for addr in addrs:
        print(addr, auto.vf.canCall(addr), addr in callers)
        assert auto.vf.canCall(addr) == (addr in callers)