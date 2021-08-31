from brownie import a


# General/shared
ADDR_0 = "0x0000000000000000000000000000000000000000"
NULL_BYTES = "0x"
E_18 = int(1e18)
INIT_ETH_BAL = 100 * E_18
BIG_NUM = 2**256 - 1


# Oracle
NORM_FACTOR = 115792089237316195423570985008687907853269984665640564039457
# Error factor since solidity and python give different answers for the same
# division calculation with very large numbers. Since the random number is used
# to choose from a relatively small list of stakers, this difference is negligible
# and won't impact the result of the executor
ERROR_FACTOR = 1.000000000000001
# Assuming ETH is $2k and AUTO is $1
INIT_AUTO_PER_ETH = 2000
INIT_AUTO_PER_ETH_WEI = INIT_AUTO_PER_ETH * E_18
# 2 gwei
INIT_GAS_PRICE_FAST = 2 * 10**9

REV_MSG_NZ_UINT = "Shared: uint input is empty"
REV_MSG_NZ_ADDR = "Shared: address input is empty"
REV_MSG_NZ_BYTES = "Shared: bytes input is empty"
REV_MSG_NZ_BYTES32 = "Shared: bytes32 input is empty"
REV_MSG_NZ_UINT_ARR = "Shared: uint arr input is empty"


# Forwarder
REV_MSG_NOT_REG = "Forw: caller not the Registry"


# Miner
INIT_REQUESTER_REWARD = 10**20
INIT_EXECUTOR_REWARD = 10**21
INIT_REFERAL_REWARD = 10**20
MAX_UPDATE_BAL = 1000 * E_18
MIN_REWARD = E_18
MIN_FUND = 10000 * E_18

REV_MSG_NO_PEND_REW = "Miner: no pending rewards"
REV_MSG_CLAIM_TOO_LARGE = "Miner: claim too large"
REV_MSG_BAL_TOO_HIGH = "Miner: AUTO bal too high"
REV_MSG_RATES_TOO_LOW = "Miner: new rates too low"
REV_MSG_FUND_TOO_LOW = "Miner: funding too low, peasant"


# Owner
REV_MSG_OWNER = "Ownable: caller is not the owner"


# StakeMan
BLOCKS_IN_EPOCH = 100
STAN_STAKE = 10000 * E_18
INIT_NUM_STAKES = 100
MAX_TEST_STAKE = INIT_NUM_STAKES * STAN_STAKE
NULL_EXEC = (ADDR_0, 0)

REV_MSG_NOT_ENOUGH_STAKE = "SM: not enough stake, peasant"
REV_MSG_NOFISH = "SM: something fishy here"
REV_MSG_NOT_STAKER = "SM: idx is not you"
REV_MSG_OUT_OF_RANGE = "Index out of range"
REV_MSG_AUTO_SET = "SM: AUTO already set"
REV_MSG_NON_AUTO_TOKEN = "SM: non-AUTO token"
REV_MSG_MISTAKE = "SM: sending by mistake"


# Registry
# EXEC_GAS_OVERHEAD_NO_REF = 40000
# EXEC_GAS_OVERHEAD_REF = 60000
GAS_OVERHEAD_AUTO = 16000
GAS_OVERHEAD_ETH = 6000
BASE_BPS = 10000
PAY_AUTO_FACTOR = 1.1
PAY_AUTO_BPS = PAY_AUTO_FACTOR * BASE_BPS
PAY_ETH_FACTOR = 1.3
PAY_ETH_BPS = PAY_ETH_FACTOR * BASE_BPS
NULL_REQ = (ADDR_0, ADDR_0, ADDR_0, NULL_BYTES, 0, 0, False, False)
# NULL_REQ_BYTES = b'\x80\x03O%\xfc\xea\xbf-\x0e\xdfP5\xb2"\xe6\x93$\x9f\x1b\xd3\x0bq\xe2\xc8\xfb\x07\x8a\xad9\x83\xd4j'
# NULL_REQ_HEX = '0x' + NULL_REQ_BYTES.hex()
NULL_HASH = '0x0000000000000000000000000000000000000000000000000000000000000000'
INIT_AUTO_REW_POOL = 10**25
INIT_GAS_PRICE_FAST = 20*10**9
CID_PREFIX_STR = '1220'
CID_PREFIX_BYTES = bytes.fromhex(CID_PREFIX_STR)
MIN_GAS = 21000

REV_MSG_TARGET = "Reg: nice try ;)"
REV_MSG_ALREADY_EXECUTED = "Reg: already executed"
REV_MSG_NOT_SAME = "Reg: request not the same"
REV_MSG_NOT_SAME_IPFS = "Reg: unveri request not the same"
REV_MSG_CANNOT_VERIFY = "Reg: cannot verify. Nice try ;)"
REV_MSG_NOT_EXEC = "Reg: not executor or expired"
REV_MSG_ETHFORCALL_NOT_MSGVALUE = "Reg: ethForCall not msg.value"
REV_MSG_ETHFORCALL_HIGH = "Reg: ethForCall too high"
REV_MSG_NOT_REQUESTER = "Reg: not the user"
REV_MSG_CALLDATA_NOT_VER = "Reg: calldata not verified"
REV_MSG_FISHY = "Reg: something fishy here"
REV_MSG_REENTRANCY = "ReentrancyGuard: reentrant call"
REV_MSG_EXPECTED_GAS = "Reg: expectedGas too high"
REV_MSG_OVERFLOW = "Integer overflow"
REV_MSG_NO_ETH_ALIVE = "Reg: no ETH while alive"


# AUTO
INIT_AUTO_SUPPLY = (10**27) + 42069
ERC1820_ETH_AMOUNT = 0.08*E_18
ERC1820_REGISTRY_ADDR = "0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24"

REV_MSG_EXCEED_BAL = "ERC777: transfer amount exceeds balance"
REV_MSG_EXCEED_ALLOWANCE = "ERC777: transfer amount exceeds allowance"


# MockTarget
REV_MSG_GOOFED = "You dun goofed boy"
REV_MSG_USER_FORW = "Not sent from userForwarder"
REV_MSG_FEE_FORW = "Not sent from feeForwarder"
REV_MSG_USER_FEE_FORW = "Not sent from userFeeForwarder"