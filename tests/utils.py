from consts import *
from brownie import web3, convert
import base58 as b58
import ipfshttpclient
from hashlib import sha256


# More concise way of getting the current block number since it's quite long
def bn():
    return web3.eth.block_number


def getEpoch(blockNum):
    return int(blockNum / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH


def getRandNum(seed):
    return web3.toInt(web3.eth.get_block(seed).hash)


def getExecutor(evmMaths, blockNum, stakes, curExec):
    if len(stakes) == 0:
        return curExec
    else:
        epoch = getEpoch(blockNum)
        # -1 because blockhash(seed) in Oracle will return 0x00 if the
        randNum = getRandNum(epoch - 1)
        i = evmMaths.getRemainder(randNum, len(stakes))
        return stakes[i], epoch


def isCurExec(exec, addr, curEpoch, stakesLen):
    if exec[1] == curEpoch:
        return exec[0] == addr
    if stakesLen == 0:
        return True

    return False


def getUpdatedExecResult(evmMaths, curHeight, stakes, curExecEpoch):
    epoch = getEpoch(curHeight)
    if epoch != curExecEpoch and len(stakes) > 0:
        randNum = getRandNum(epoch - 1)
        idx = evmMaths.getRemainder(randNum, len(stakes))
        return (epoch, randNum, idx, stakes[idx])
    else:
        return (epoch, 0, 0, ADDR_0)


def getFirstIndexes(stakes, val, n):
    cntr = 0
    idxs = []
    # So it doesn't change the list used as input to this fcn
    newStakes = stakes.copy()

    for i in range(n):
        idx = newStakes.index(val)
        idxs.append(idx)
        newStakes[idx] = newStakes[-1]
        newStakes = newStakes[:-1]


    # for i, el in enumerate(newStakes):
    #     if el == val:
    #         idxs.append(i)
    #         cntr += 1
    #         if cntr == n:
    #             break
    
    
    # Shouldn't be a situation where fewer occurances are
    # found than expected
    assert len(idxs) == n

    return idxs, newStakes


def unstakeErrors(stakes, idxs, staker):
    # So it doesn't change the list used as input to this fcn
    newStakes = stakes.copy()

    for i in idxs:
        if i > len(newStakes)-1:
            return True, None, None
        elif newStakes[i] != staker:
            return None, True, None
        newStakes[i] = newStakes[-1]
        newStakes = newStakes[:-1]
    
    return False, False, newStakes


def getModStakes(stakes, staker, numStakes, isStaking):
    if isStaking:
        return stakes + ([staker] * numStakes)
    else:
        idxs = []
        # So it doesn't change the list used as input to this fcn
        newStakes = stakes.copy()
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


def keccakReq(auto, req):
    return web3.keccak(auto.r.getReqBytes(req)).hex()


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


def checkAreCallers(forwarder, addrs, callers):
    addrs = [str(ad) for ad in addrs]
    callers = [str(c) for c in callers]
    for addr in addrs:
        assert forwarder.canCall(addr) == (addr in callers)


def hexStrPad(num):
    numStr = hex(num)
    numStr = numStr[2:] if numStr[:2] == "0x" else numStr
    return ("0" * (64 - len(numStr))) + numStr